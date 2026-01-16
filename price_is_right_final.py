import logging
import queue
import threading
import time
import gradio as gr
from deal_agent_framework import DealAgentFramework
from agents.deals import Opportunity, Deal
from log_utils import reformat
import plotly.graph_objects as go

import os
import requests
import json
from urllib.parse import urlparse
from dotenv import load_dotenv
from dotenv import load_dotenv
load_dotenv()
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_USER = "sushmaaditya717@gmail.com"
EMAIL_PASSWORD = "ethr qfod nnub hjbo"

def send_email_alert(opp):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_USER
        msg['Subject'] = f"🚨 High Value Deal Alert: {opp.deal.product_description[:30]}..."

        body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #e9ecef;">
              <h2 style="color: #2c3e50; margin-top: 0;">🚨 High Value Deal Found!</h2>
              <hr style="border: 0; border-top: 1px solid #dee2e6;">
              <p><strong>Competitor:</strong> {urlparse(opp.deal.url).netloc.replace('www.', '')}</p>
              <p><strong>Product:</strong> {opp.deal.product_description}</p>
              <p><strong>Gross Difference:</strong> <span style="color: #27ae60; font-weight: bold; font-size: 1.2em;">₹{opp.discount:.2f}</span></p>
              <br>
              <a href="{opp.deal.url}" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">View Deal Link</a>
            </div>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, EMAIL_USER, text)
        server.quit()
        print(f"Email sent for {opp.deal.product_description[:20]}")
    except Exception as e:
        print(f"Failed to send email: {e}")



class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(self.format(record))


def html_for(log_data):
    output = '<br>'.join(log_data[-18:])
    return f"""
    <div id="scrollContent" style="height: 400px; overflow-y: auto; border: 1px solid #ccc; background-color: #222229; padding: 10px;">
    {output}
    </div>
    """


def setup_logging(log_queue):
    handler = QueueHandler(log_queue)
    formatter = logging.Formatter(
        "[%(asctime)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S %z",
    )
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


LLAMA_ENDPOINT = "http://localhost:11434/api/generate"  # OLLAMA endpoint
LLAMA_MODEL = "llama3.2"                                 # Your model name


# ======================================================
# CALL LOCAL LLaMA
# ======================================================
def call_llama(prompt):

    # 1. Build correct payload based on endpoint
    if "11434" in LLAMA_ENDPOINT:   # OLLAMA
        payload = {"model": LLAMA_MODEL, "prompt": prompt, "stream": False}

    elif "/v1/" in LLAMA_ENDPOINT:  # LM STUDIO (OpenAI format)
        payload = {
            "model": LLAMA_MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }

    else:                            # FALLBACK (llama.cpp)
        payload = {"model": LLAMA_MODEL, "prompt": prompt}

    # Call model
    r = requests.post(LLAMA_ENDPOINT, json=payload)
    raw = r.text.strip()

    # 2. Try direct JSON parse
    try:
        data = r.json()
        return (
            data.get("response") or
            (data.get("choices", [{}])[0].get("message", {}).get("content")) or
            data.get("content")
        )
    except:
        pass

    # 3. FIX multi-chunk JSON (Ollama sometimes outputs two JSON blocks)
    cleaned = raw.replace("}\n{", "},{").replace("}{", "},{")
    cleaned = "[" + cleaned + "]"

    try:
        chunk = json.loads(cleaned)[0]
        return (
            chunk.get("response") or
            chunk.get("content") or
            (chunk.get("choices", [{}])[0].get("message", {}).get("content"))
        )
    except:
        return f"⚠ Invalid LLM output:\n{raw}"

def reasons_for_item(desc):
    prompt = f"""
Analyze why this product is a "Top Seller" in current market conditions.
Provide 3 distinct, professional insights focusing on value proposition, competitive advantage, or consumer demand.

Product:
{desc}

Constraints:
- Return exactly 3 short, punchy bullet points.
- Use professional business tone.
- No introductory text (e.g. "Here are the reasons").
"""
    return call_llama(prompt)


def reasons_for_all_items():
    with open("memory.json", "r", encoding="utf-8") as f:
        mem = json.load(f)

    last_items = mem[-5:]

    html = """
    <style>
    .card {
        background: #ffffff;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease;
    }
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    }
    .title {
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 16px;
        color: #1e293b;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 12px;
        line-height: 1.4;
    }
    .subtitle {
        font-size: 11px;
        text-transform: uppercase;
        color: #64748b;
        font-weight: 700;
        margin-bottom: 12px;
        letter-spacing: 0.05em;
    }
    .bullet {
        font-size: 14px;
        margin-left: 0;
        margin-bottom: 10px;
        color: #334155;
        display: flex;
        align-items: start;
        line-height: 1.6;
    }
    .bullet strong {
        color: #4f46e5;
        font-weight: 600;
        margin-right: 4px;
    }
    .icon-box {
        background: #eef2ff;
        color: #4f46e5;
        min-width: 20px;
        height: 20px;
        border-radius: 5px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 12px;
        font-size: 12px;
        margin-top: 2px;
        flex-shrink: 0;
    }
    </style>

    <div style="margin-bottom: 24px">
        <h2 style="color: #1e293b; margin: 0; font-size: 20px; display: flex; align-items: center; gap: 10px; border: none;">
            <span>🧠</span> Market Intelligence Analysis
        </h2>
        <p style="color: #64748b; margin-top: 4px; font-size: 14px; margin-left: 36px;">Deep dive into top-performing products</p>
    </div>
    """

    for item in last_items:
        desc = item["deal"]["product_description"]
        reason = reasons_for_item(desc)
        
        # Regex to handle bold text: **text** -> <strong>text</strong>
        import re
        formatted_reason = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', reason)

        bullets = ""
        for line in formatted_reason.split("\n"):
            line = line.strip().lstrip("-").lstrip("•").strip()
            if line:
                bullets += f"""
                <div class='bullet'>
                    <div class="icon-box">✓</div>
                    <div>{line}</div>
                </div>
                """

        short_title = desc[:100] + "..." if len(desc) > 100 else desc

        html += f"""
        <div class='card'>
            <div class='title'>{short_title}</div>
            <div class='subtitle'>Key Value Drivers</div>
            {bullets}
        </div>
        """

    return html





class App:

    def __init__(self):
        self.agent_framework = None
        self.sent_emails = set()

    def get_agent_framework(self):
        if not self.agent_framework:
            self.agent_framework = DealAgentFramework()
            self.agent_framework.init_agents_as_needed()
        return self.agent_framework

    def run(self):
    
        def table_for(opps):
            rows = []
            for opp in opps:
                try:
                    domain = urlparse(opp.deal.url).netloc.replace("www.", "")
                except:
                    domain = "Unknown"
                
                # Truncate desc for table compactness
                desc = opp.deal.product_description
                if len(desc) > 120:
                    desc = desc[:117] + "..."

                # Truncate URL text but keep link
                url_text = opp.deal.url
                if len(url_text) > 45:
                    url_text = url_text[:42] + "..."

                rows.append([
                    desc,
                    f"₹{opp.deal.price:.2f}",
                    f"₹{opp.estimate:.2f}",
                    f"₹{opp.discount:.2f}",
                    domain,
                    f"[{url_text}]({opp.deal.url})",
                ])
            return rows
        
        def update_output(log_data, log_queue, result_queue):
            initial_result = table_for(self.get_agent_framework().memory)
            final_result = None
            while True:
                try:
                    message = log_queue.get_nowait()
                    log_data.append(reformat(message))
                    yield log_data, html_for(log_data), final_result or initial_result
                except queue.Empty:
                    try:
                        final_result = result_queue.get_nowait()
                        yield log_data, html_for(log_data), final_result or initial_result
                    except queue.Empty:
                        if final_result is not None:
                            break
                        time.sleep(0.1)
        
        def get_plot():
            documents, vectors, colors = DealAgentFramework.get_plot_data(max_datapoints=1000)
            fig = go.Figure(
                data=[go.Scatter3d(
                    x=vectors[:, 0],
                    y=vectors[:, 1],
                    z=vectors[:, 2],
                    mode='markers',
                    marker=dict(size=2, color=colors, opacity=0.7),
                )]
            )
            fig.update_layout(
                scene=dict(
                    xaxis_title='x',
                    yaxis_title='y',
                    zaxis_title='z',
                    aspectmode='manual',
                    aspectratio=dict(x=2.2, y=2.2, z=1),
                    camera=dict(eye=dict(x=1.6, y=1.6, z=0.8))
                ),
                height=350,
                margin=dict(r=5, b=1, l=5, t=2)
            )
            return fig
        
        def do_run():
            new_opportunities = self.get_agent_framework().run()
            
            # Check for high value deals to email
            for opp in new_opportunities:
                if opp.discount > 20000 and opp.deal.url not in self.sent_emails:
                    threading.Thread(target=send_email_alert, args=(opp,)).start()
                    self.sent_emails.add(opp.deal.url)
                    
            return table_for(new_opportunities)
        
        def run_with_logging(initial_log_data):
            log_queue = queue.Queue()
            result_queue = queue.Queue()
            setup_logging(log_queue)
        
            def worker():
                result = do_run()
                result_queue.put(result)
        
            thread = threading.Thread(target=worker)
            thread.start()
        
            for log_data, output, final_result in update_output(initial_log_data, log_queue, result_queue):
                yield log_data, output, final_result
        
        def do_select(selected_index: gr.SelectData):
            opportunities = self.get_agent_framework().memory
            row = selected_index.index[0]
            if row < len(opportunities):
                opportunity = opportunities[row]
                if self.get_agent_framework().planner:
                    self.get_agent_framework().planner.messenger.alert(opportunity)
        
        def filter_status_update(*args):
            """Show a status update when filters change"""
            return "✓ Filters updated - Click refresh to apply"
        
        # ===============================
        # 2. UI STARTS HERE
        # ===============================
        
        # customized business theme - LIGHT PROFESSIONAL & COMPACT
        business_theme = gr.themes.Soft(
            primary_hue="indigo",
            neutral_hue="slate",
            text_size=gr.themes.sizes.text_sm,
            spacing_size=gr.themes.sizes.spacing_sm,
            radius_size=gr.themes.sizes.radius_sm,
            font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
        ).set(
            body_background_fill="#f8fafc",     # Light Slate background
            block_background_fill="#ffffff",    # White blocks
            block_border_width="1px",
            block_border_color="#cbd5e1",       # Light gray border
            block_label_text_color="#64748b",   # Muted slate text
            block_title_text_color="#0f172a",   # Dark slate title
            body_text_color="#334155",          # Default text (Dark Slate)
            checkbox_background_color="#f1f5f9",
            checkbox_border_color="#cbd5e1",
            checkbox_label_text_color="#334155",
            button_primary_background_fill="#4f46e5", # Indigo Brand
            button_primary_background_fill_hover="#4338ca",
            button_primary_text_color="white",
        )
        
        custom_css = """
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #1e293b;
        }
        .pricer-title {
            text-align: center;
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 1.5rem;
            background: linear-gradient(135deg, #4f46e5, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            text-shadow: 0 10px 20px rgba(79, 70, 229, 0.1);
        }
        
        /* Table Styles - Force Light Mode & Professional */
        .gradio-container table {
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
            border-collapse: collapse;
            width: 100%;
        }
        
        thead th {
            background-color: #f1f5f9 !important;
            color: #475569 !important;
            font-family: 'Inter', sans-serif;
            font-weight: 700 !important;
            text-transform: uppercase;
            font-size: 0.75rem !important;
            letter-spacing: 0.05em;
            padding: 12px 16px !important;
            border-bottom: 2px solid #e2e8f0 !important;
            text-align: left !important;
        }
        
        tbody tr {
            background-color: #ffffff !important;
            border-bottom: 1px solid #e2e8f0;
            transition: background-color 0.2s;
        }
        
        tbody tr:hover {
            background-color: #f8fafc !important;
        }
        
        tbody td {
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem !important;
            color: #334155 !important;
            padding: 12px 16px !important;
            vertical-align: middle !important;
            border-bottom: 1px solid #e2e8f0;
        }
        
        /* Fix Link Color in Table */
        tbody td a {
            color: #4f46e5 !important; 
            text-decoration: none;
            font-weight: 500;
        }
        tbody td a:hover {
            text-decoration: underline;
        }

        input[type="checkbox"] {
            border-radius: 3px !important;
        }
        
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f5f9; 
        }
        ::-webkit-scrollbar-thumb {
            background: #cbd5e1; 
            border-radius: 3px;
        }
        """

        with gr.Blocks(title="PRICER", theme=business_theme, css=custom_css, fill_width=True) as ui:
            
            # SITE TITLE
            gr.Markdown("<div class='pricer-title'>PRICER</div>")
        
            # TOP FILTER PANEL
            with gr.Row():
        
                # ------ LEFT FILTERS ------
                with gr.Column(scale=1):
        
                    preference = gr.Dropdown(
                        label="Market Intelligence Sort",
                        choices=["Lowest Competitor Price", "Highest Margin Potential", "Recently Scanned", "Listing Timestamp"],
                        value=[],
                        multiselect=True,
                        interactive=True
                    )
        
                    with gr.Row():
                        time_constraint = gr.Dropdown(
                            label="Analysis Window",
                            choices=["Last 24h", "Last 72h", "Current Week", "Current Month", "Historical Data"],
                            value=["Historical Data"],
                            multiselect=True,
                            interactive=True,
                            scale=1
                        )
            
                        price_filter = gr.Dropdown(
                            label="Pricing Segment",
                            choices=["Entry Level (< 1k)", "Mass Market (< 10k)", "Mid-Tier (10k-20k)", "Premium Tier (> 25k)"],
                            value=[],
                            multiselect=True,
                            interactive=True,
                            scale=1
                        )
        
                    with gr.Row():
                        ratings_filter = gr.Dropdown(
                            label="Vendor Reliability",
                            choices=["Top Rated (4★+)", "Mid Rated (3-4★)", "All Vendors"],
                            value=["All Vendors"],
                            multiselect=True,
                            interactive=True,
                            scale=1
                        )
            
                        delivery_filter = gr.Dropdown(
                            label="Logistics",
                            choices=["Free Shipping Only", "All Options"],
                            value=["All Options"],
                            multiselect=True,
                            interactive=True,
                            scale=1
                        )
        
                    mfg_filter = gr.Dropdown(
                        label="Product Lifecycle",
                        choices=["Current Gen", "Last Gen", "All Lifecycle"],
                        value=["All Lifecycle"],
                        multiselect=True,
                        interactive=True
                    )
        
                # ------ RIGHT FILTERS ------
                with gr.Column(scale=1):
        
                    domain = gr.Dropdown(
                        label="Target Verticals",
                        choices=[
                            "All Verticals", "Mobile Devices", "Computing", "Audio", "Consumer Electronics", "Gaming Systems",
                            "Apparel", "Fashion Retail", "Footwear", "Horology", "Home Goods", "Sporting Goods",
                            "Personal Care", "FMCG", "Major Appliances", "Tablets",
                            "Imaging", "IT Peripherals", "Entertainment Systems", "Media & Books", "Furniture",
                            "Toys/Hobby", "Smart Wearables"
                        ],
                        value=["All Verticals"],
                        multiselect=True,
                        interactive=True
                    )
        
                    # Bubble chart in accordion (safe)
                    with gr.Accordion("Competitor Deal Distribution", open=False):
        
                        import plotly.express as px
                        import pandas as pd
        
                        df = pd.DataFrame({
                            "competitor": ["Amazon", "Flipkart", "Croma", "Myntra", "Reliance Digital", "Tata Cliq"],
                            "active_deals": [120, 95, 40, 60, 35, 25],
                        })
        
                        bubble_fig = px.scatter(
                            df,
                            x="competitor",
                            y="active_deals",
                            size="active_deals",
                            color="competitor",
                            size_max=60,
                            height=320,
                            labels={"active_deals": "Active Deals", "competitor": "Competitor Store"}
                        )
        
                        bubble_fig.update_layout(
                            paper_bgcolor="white",
                            plot_bgcolor="white",
                            font=dict(color="black"),
                            height=320,
                            margin=dict(l=10, r=10, t=10, b=10),
                            showlegend=False
                        )
        
                        bubble_plot = gr.Plot(value=bubble_fig, show_label=False)
        
            # Filter status indicator
            filter_status = gr.Textbox(
                value="",
                show_label=False,
                interactive=False,
                visible=True,
                container=False
            )
        
            # REFRESH BUTTON
            with gr.Row():
                refresh_button = gr.Button("🔄 Apply Filters & Refresh Deals", variant="primary")
        
            log_data = gr.State([])
        
            # TABLE
            with gr.Column():
                gr.Markdown("### Market Opportunities", elem_id="table-header")
                
                opportunities_dataframe = gr.Dataframe(
                    headers=["Deals found", "Competitor Price", "Market Value", "Gross Difference", "Source", "Link"],
                    wrap=True,
                    column_widths=[10, 1, 1, 1, 1, 5],
                    row_count=10,
                    col_count=6,
                    datatype=["str", "str", "str", "str", "str", "markdown"],
                    max_height=400,
                    interactive=False
                )




            with gr.Accordion("LLM Market Intelligence — Top Selling Analysis ", open=False):
            
                reasons_btn = gr.Button("Generate Top Selling Analysis")
                reasons_output = gr.HTML("Click the button to generate insights.\n")
            
                reasons_btn.click(
                    fn=reasons_for_all_items,
                    inputs=None,
                    outputs=reasons_output
                )

        
            # LOGS LEFT + 3D PLOT RIGHT
            with gr.Row():
        
                with gr.Column(scale=1):
                    logs = gr.HTML()
        
                with gr.Column(scale=1):
                    plot = gr.Plot(value=get_plot(), show_label=False)
        
        
            # ===============================
            # 3. EVENTS - Connect all filters
            # ===============================
            
            # Make all checkboxes show status update on change
            all_filters = [
                preference, time_constraint, price_filter, 
                ratings_filter, delivery_filter, mfg_filter, domain
            ]
            
            for filter_component in all_filters:
                filter_component.change(
                    fn=filter_status_update,
                    inputs=all_filters,
                    outputs=filter_status
                )
            
            # Main refresh and load events
            ui.load(
                fn=run_with_logging, 
                inputs=[log_data], 
                outputs=[log_data, logs, opportunities_dataframe]
            )
        
            timer = gr.Timer(value=300, active=True)
            timer.tick(
                fn=run_with_logging, 
                inputs=[log_data], 
                outputs=[log_data, logs, opportunities_dataframe]
            )
        
            refresh_button.click(
                fn=run_with_logging, 
                inputs=[log_data], 
                outputs=[log_data, logs, opportunities_dataframe]
            )
        
            opportunities_dataframe.select(do_select)
        
        
        ui.launch(share=False, inbrowser=True)



if __name__ == "__main__":
    App().run()