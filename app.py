import os
import json
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================================
# 1. LOAD API KEY
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error(
        "Gemini API key not found.\n\n"
        "Please create a .env file in the same folder as app.py "
        "and add:\n\n"
        "GEMINI_API_KEY=YOUR_API_KEY"
    )
    st.stop()


# ============================================================
# 2. GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)

MODEL = "gemini-3.8-flash"


# ============================================================
# 3. PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Helpdesk Ticket Router",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 4. SESSION STATE
# ============================================================

# Main ticket chatbot history
if "ticket_messages" not in st.session_state:
    st.session_state.ticket_messages = []


# Small AI assistant history
if "assistant_messages" not in st.session_state:
    st.session_state.assistant_messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! 👋 I'm your AI Assistant.\n\n"
                "I can help with booking questions, "
                "cancellations, payments, refunds, and "
                "general support."
            )
        }
    ]


# Ticket routing history
if "routing_logs" not in st.session_state:
    st.session_state.routing_logs = []


# Ticket number
if "ticket_number" not in st.session_state:
    st.session_state.ticket_number = 1001


# ============================================================
# 5. KNOWLEDGE BASE
# ============================================================

KNOWLEDGE_BASE = {

    "Booking Confirmation": {
        "department": "Reservation Support",
        "solution": (
            "Check the registered email address and spam folder. "
            "Verify the booking status. If the booking is successful, "
            "the confirmation can be resent."
        )
    },

    "Booking Cancellation": {
        "department": "Cancellation Team",
        "solution": (
            "Check the booking cancellation policy and current "
            "booking status. Verify whether cancellation charges apply."
        )
    },

    "Booking Modification": {
        "department": "Reservation Support",
        "solution": (
            "Check whether the booking supports date, time, or "
            "passenger-detail changes and whether any modification "
            "charges apply."
        )
    },

    "Payment Issue": {
        "department": "Payments & Billing",
        "solution": (
            "Verify the payment transaction and booking status. "
            "For duplicate charges, compare the transaction references "
            "before starting a payment investigation."
        )
    },

    "Refund Issue": {
        "department": "Refund Team",
        "solution": (
            "Check the refund status, original payment method, "
            "and expected refund processing timeline."
        )
    },

    "Account / Login Issue": {
        "department": "Account & IT Support",
        "solution": (
            "Check the account status and login credentials. "
            "Use the password-reset process when necessary."
        )
    },

    "General Booking Request": {
        "department": "Customer Support",
        "solution": (
            "Please provide the booking reference and explain "
            "the problem so the support team can investigate."
        )
    }
}


# ============================================================
# 6. CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       MAIN PAGE BACKGROUND
       ======================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 85% 10%,
                rgba(187, 214, 248, 0.30),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #edf5ff 0%,
                #f6f1ff 52%,
                #eef8ff 100%
            );
    }


    /* ========================================================
       LIGHT PURPLE SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {
        background: #e8ddf5;
        border-right: 1px solid #d8c8e8;
    }

    section[data-testid="stSidebar"] * {
        color: #342442;
    }


    /* ========================================================
       MAIN TITLE
       ======================================================== */

    .main-title {
        font-size: 38px;
        font-weight: 800;
        color: #39274e;
        margin-bottom: 4px;
    }

    .main-subtitle {
        font-size: 16px;
        color: #6b6173;
        margin-bottom: 25px;
    }


    /* ========================================================
       WELCOME CARD
       ======================================================== */

    .welcome-card {
        background: rgba(255, 255, 255, 0.90);
        border: 1px solid #ddd6e7;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 8px 25px rgba(70, 53, 87, 0.06);
    }


    /* ========================================================
       ANALYSIS CARD
       ======================================================== */

    .analysis-card {
        background: rgba(255, 255, 255, 0.94);
        border: 1px solid #ddd6e7;
        border-radius: 18px;
        padding: 20px;
        margin-top: 12px;
        box-shadow: 0 5px 20px rgba(70, 53, 87, 0.05);
    }


    /* ========================================================
       DASHBOARD CARDS
       ======================================================== */

    .metric-card {
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid #ddd6e7;
        border-radius: 16px;
        padding: 18px;
        text-align: center;
    }

    .metric-number {
        font-size: 28px;
        font-weight: 800;
        color: #50356e;
    }

    .metric-label {
        font-size: 13px;
        color: #756b7b;
    }


    /* ========================================================
       FLOATING AI ASSISTANT BUTTON
       ======================================================== */

    .st-key-ai_assistant {
        position: fixed;
        right: 24px;
        bottom: 24px;
        z-index: 9999;
    }

    .st-key-ai_assistant button {
        width: 62px !important;
        height: 62px !important;
        min-width: 62px !important;
        border-radius: 50% !important;

        background: #8f6bb8 !important;
        color: white !important;

        border: 3px solid white !important;

        box-shadow:
            0 8px 26px rgba(72, 49, 100, 0.25) !important;

        font-size: 25px !important;
        padding: 0 !important;
    }

    .st-key-ai_assistant button:hover {
        transform: scale(1.06);
    }


    /* ========================================================
       ASSISTANT BUTTONS
       ======================================================== */

    .assistant-quick button {
        font-size: 12px !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 7. CREATE TICKET ID
# ============================================================

def create_ticket_id():

    ticket_id = f"TKT-{st.session_state.ticket_number}"

    st.session_state.ticket_number += 1

    return ticket_id


# ============================================================
# 8. KNOWLEDGE BASE LOOKUP
# ============================================================

def get_knowledge_solution(category):

    return KNOWLEDGE_BASE.get(
        category,
        KNOWLEDGE_BASE["General Booking Request"]
    )["solution"]


# ============================================================
# 9. AI TICKET ANALYSIS
# ============================================================

def analyze_ticket(user_message):

    categories = list(
        KNOWLEDGE_BASE.keys()
    )

    prompt = f"""
You are an AI Helpdesk Ticket Router.

Analyze the customer's booking support request.

Allowed categories:

{categories}

Available departments:

Reservation Support
Cancellation Team
Payments & Billing
Refund Team
Account & IT Support
Customer Support

Return ONLY valid JSON using this structure:

{{
    "category": "one allowed category",
    "priority": "Low, Medium, or High",
    "issue": "short description",
    "summary": "one sentence summary",
    "confidence": "High, Medium, or Low",
    "reason": "short reason"
}}

Priority rules:

HIGH:
- urgent
- emergency
- immediate problem
- travel very soon
- cannot use booking
- serious payment problem
- account blocked

MEDIUM:
- payment issue
- cancellation issue
- booking confirmation issue
- modification issue
- important problem

LOW:
- general question
- information request
- normal non-urgent request

Customer message:

{user_message}
"""

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=500,
                response_mime_type="application/json"
            )
        )

        result = json.loads(
            response.text
        )

        category = result.get(
            "category",
            "General Booking Request"
        )

        if category not in KNOWLEDGE_BASE:
            category = "General Booking Request"

        priority = result.get(
            "priority",
            "Low"
        )

        if priority not in [
            "Low",
            "Medium",
            "High"
        ]:
            priority = "Low"

        department = KNOWLEDGE_BASE[
            category
        ]["department"]

        solution = get_knowledge_solution(
            category
        )

        return {
            "category": category,
            "priority": priority,
            "department": department,
            "issue": result.get(
                "issue",
                "Booking support issue"
            ),
            "summary": result.get(
                "summary",
                user_message
            ),
            "confidence": result.get(
                "confidence",
                "Medium"
            ),
            "reason": result.get(
                "reason",
                "The request was analyzed by AI."
            ),
            "solution": solution
        }

    except Exception as e:

        return {
            "category": "General Booking Request",
            "priority": "Low",
            "department": "Customer Support",
            "issue": user_message,
            "summary": user_message,
            "confidence": "Low",
            "reason": "Fallback classification was used.",
            "solution": get_knowledge_solution(
                "General Booking Request"
            ),
            "error": str(e)
        }


# ============================================================
# 10. MAIN TICKET RESPONSE
# ============================================================

def generate_ticket_response(
    user_message,
    analysis,
    ticket_id
):

    prompt = f"""
You are the customer-facing AI Helpdesk Ticket Router.

Customer message:

{user_message}

Ticket information:

Category:
{analysis["category"]}

Priority:
{analysis["priority"]}

Department:
{analysis["department"]}

Issue:
{analysis["issue"]}

Suggested resolution:
{analysis["solution"]}

Ticket ID:
{ticket_id}

Write a friendly response using simple English.

Include:

- acknowledgement
- category
- priority
- routed department
- suggested resolution
- ticket ID

Do not say that a real booking was changed,
cancelled, refunded, or confirmed.
"""

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.4,
                max_output_tokens=600
            )
        )

        return response.text

    except Exception:

        return (
            f"I understand your booking issue.\n\n"
            f"**Ticket ID:** {ticket_id}\n\n"
            f"**Category:** {analysis['category']}\n\n"
            f"**Priority:** {analysis['priority']}\n\n"
            f"**Department:** {analysis['department']}\n\n"
            f"**Suggested Resolution:** "
            f"{analysis['solution']}"
        )


# ============================================================
# 11. SMALL AI ASSISTANT RESPONSE
# ============================================================

def get_assistant_response(user_message):

    recent_messages = (
        st.session_state.assistant_messages[-10:]
    )

    conversation = ""

    for message in recent_messages:

        conversation += (
            f"{message['role'].upper()}: "
            f"{message['content']}\n"
        )

    prompt = f"""
You are the small AI Assistant inside
an AI Helpdesk Ticket Router.

You are a friendly booking support assistant.

You can help with:

- booking confirmation
- booking cancellation
- booking changes
- payment questions
- refund questions
- account/login questions
- general booking questions

Rules:

1. Be friendly.
2. Use simple English.
3. Keep the answer reasonably short.
4. Ask a follow-up question when needed.
5. Help the customer understand what to do.
6. Never invent booking information.
7. Never claim that a real booking was
   changed, cancelled, refunded, or confirmed.
8. You are the supporting AI Assistant.
9. The main chatbot is responsible for
   creating and routing tickets.
10. Do not create fake ticket IDs.

Previous conversation:

{conversation}

New customer message:

{user_message}

Give a helpful response.
"""

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.5,
                max_output_tokens=400
            )
        )

        return response.text

    except Exception:

        return (
            "Sorry, I couldn't connect to the AI service "
            "right now. Please try again."
        )


# ============================================================
# 12. PROCESS TICKET
# ============================================================

def process_ticket(user_message):

    analysis = analyze_ticket(
        user_message
    )

    ticket_id = create_ticket_id()

    timestamp = datetime.now().strftime(
        "%d-%m-%Y %I:%M %p"
    )

    routing_log = {
        "ticket_id": ticket_id,
        "time": timestamp,
        "message": user_message,
        "category": analysis["category"],
        "priority": analysis["priority"],
        "department": analysis["department"],
        "status": "Routed",
        "summary": analysis["summary"]
    }

    st.session_state.routing_logs.append(
        routing_log
    )

    response = generate_ticket_response(
        user_message,
        analysis,
        ticket_id
    )

    return (
        ticket_id,
        analysis,
        response
    )


# ============================================================
# 13. SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="text-align:center; padding:8px;">
            <div style="font-size:48px;">🎫</div>
            <div style="
                font-size:24px;
                font-weight:800;
                color:#342442;
            ">
                AI Helpdesk
            </div>
            <div style="
                font-size:13px;
                color:#6c6074;
            ">
                Ticket Router
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "💬 Chat Support",
            "📊 Dashboard",
            "📝 Ticket History"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("### 🧠 AI Workflow")

    st.markdown(
        """
        **AI Assistant**

        Natural conversation

        ↓

        **Ticket Classification**

        ↓

        **Priority Detection**

        ↓

        **Department Routing**

        ↓

        **Knowledge Base**

        ↓

        **Ticket History**
        """
    )

    st.divider()

    if st.button(
        "🗑️ Clear Main Chat",
        use_container_width=True
    ):

        st.session_state.ticket_messages = []

        st.rerun()


# ============================================================
# 14. MAIN CHAT SUPPORT
# ============================================================

if page == "💬 Chat Support":

    st.markdown(
        "## 🎫 AI Helpdesk Ticket Router"
    )

    st.caption(
        "Describe your booking problem and AI will "
        "classify and route your support ticket."
    )

    # Welcome section
    if not st.session_state.ticket_messages:
        st.subheader("👋 Welcome!")

        st.write(
            "Tell me about your booking problem. "
            "The AI will understand your request, "
            "classify the ticket and route it to "
            "the appropriate team."
        )

        st.markdown("**Example:**")

        st.info(
            "I booked a flight yesterday but I haven't "
            "received my confirmation email."
        )

        st.write("")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.info(
                "✈️ **Booking**\n\n"
                "Confirmation • Cancellation • Changes"
            )

        with c2:
            st.warning(
                "💳 **Payment**\n\n"
                "Payment failure • Duplicate charge"
            )

        with c3:
            st.success(
                "💰 **Refund**\n\n"
                "Refund pending • Missing refund"
            )

    # Display existing ticket messages
    for message in st.session_state.ticket_messages:

        if message["role"] == "user":

            with st.chat_message("user", avatar="👤"):
                st.write(message["content"])

        else:

            with st.chat_message("assistant", avatar="🎫"):

                st.markdown(message["content"])

                analysis = message.get("analysis")

                if analysis:

                    st.markdown(
                        f"""
                        <div class="analysis-card">

                            <h4>🔎 AI Ticket Analysis</h4>

                            <p>
                                <b>🏷️ Category:</b>
                                {analysis["category"]}
                            </p>

                            <p>
                                <b>🚦 Priority:</b>
                                {analysis["priority"]}
                            </p>

                            <p>
                                <b>📂 Department:</b>
                                {analysis["department"]}
                            </p>

                            <p>
                                <b>🧠 Confidence:</b>
                                {analysis["confidence"]}
                            </p>

                            <p>
                                <b>🔍 Issue:</b>
                                {analysis["issue"]}
                            </p>

                            <p>
                                <b>💡 Suggested Resolution:</b>
                                {analysis["solution"]}
                            </p>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    # Main chatbot input
    user_input = st.chat_input(
        "Describe your booking problem..."
    )

    if user_input:

        st.session_state.ticket_messages.append(
            {
                "role": "user",
                "content": user_input
            }
        )

        ticket_id, analysis, response = process_ticket(
            user_input
        )

        st.session_state.ticket_messages.append(
            {
                "role": "assistant",
                "content": response,
                "analysis": analysis,
                "ticket_id": ticket_id
            }
        )

        st.rerun()




# ============================================================
# 15. DASHBOARD
# ============================================================

elif page == "📊 Dashboard":

    st.markdown(
        '<div class="main-title">'
        '📊 Routing Dashboard'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="main-subtitle">'
        'Overview of AI-routed support tickets.'
        '</div>',
        unsafe_allow_html=True
    )

    total = len(
        st.session_state.routing_logs
    )

    high = sum(
        1
        for ticket in st.session_state.routing_logs
        if ticket["priority"] == "High"
    )

    medium = sum(
        1
        for ticket in st.session_state.routing_logs
        if ticket["priority"] == "Medium"
    )

    low = sum(
        1
        for ticket in st.session_state.routing_logs
        if ticket["priority"] == "Low"
    )


    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.markdown(
            f"""
            <div class="metric-card">

                <div class="metric-number">
                    {total}
                </div>

                <div class="metric-label">
                    Total Tickets
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            f"""
            <div class="metric-card">

                <div class="metric-number">
                    {high}
                </div>

                <div class="metric-label">
                    High Priority
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:

        st.markdown(
            f"""
            <div class="metric-card">

                <div class="metric-number">
                    {medium}
                </div>

                <div class="metric-label">
                    Medium Priority
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:

        st.markdown(
            f"""
            <div class="metric-card">

                <div class="metric-number">
                    {low}
                </div>

                <div class="metric-label">
                    Low Priority
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    st.write("")

    st.subheader(
        "📂 Department Routing"
    )

    department_counts = {}

    for ticket in st.session_state.routing_logs:

        department = ticket["department"]

        department_counts[department] = (
            department_counts.get(
                department,
                0
            ) + 1
        )


    if department_counts:

        for department, count in (
            department_counts.items()
        ):

            st.write(
                f"📂 **{department}** → "
                f"{count} ticket(s)"
            )

    else:

        st.info(
            "No tickets have been routed yet."
        )


# ============================================================
# 16. TICKET HISTORY
# ============================================================

elif page == "📝 Ticket History":

    st.markdown(
        '<div class="main-title">'
        '📝 Ticket History'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="main-subtitle">'
        'Previously analyzed and routed tickets.'
        '</div>',
        unsafe_allow_html=True
    )


    if not st.session_state.routing_logs:

        st.info(
            "No tickets yet. Create one from Chat Support."
        )

    else:

        for ticket in reversed(
            st.session_state.routing_logs
        ):

            with st.expander(
                f"🎫 {ticket['ticket_id']} | "
                f"{ticket['category']} | "
                f"{ticket['priority']}"
            ):

                st.write(
                    f"**Time:** {ticket['time']}"
                )

                st.write(
                    f"**Category:** {ticket['category']}"
                )

                st.write(
                    f"**Priority:** {ticket['priority']}"
                )

                st.write(
                    f"**Department:** {ticket['department']}"
                )

                st.write(
                    f"**Status:** {ticket['status']}"
                )

                st.write(
                    f"**Summary:** {ticket['summary']}"
                )

                st.write(
                    "**Original User Request:**"
                )

                st.info(
                    ticket["message"]
                )


# ============================================================
# 17. FLOATING AI ASSISTANT BUTTON + POPUP
# ============================================================

assistant_popup = st.popover(
    "🤖",
    key="ai_assistant",
    help="Open AI Assistant",
    width=380
)


# ============================================================
# 18. AI ASSISTANT POPUP CONTENT
# ============================================================

with assistant_popup:

    st.markdown(
        "### 🤖 AI Assistant"
    )

    st.caption(
        "Your small booking support assistant"
    )

    st.divider()


    # --------------------------------------------------------
    # ASSISTANT CHAT
    # --------------------------------------------------------

    for message in (
        st.session_state.assistant_messages
    ):

        if message["role"] == "assistant":

            with st.chat_message(
                "assistant",
                avatar="🤖"
            ):

                st.markdown(
                    message["content"]
                )

        else:

            with st.chat_message(
                "user",
                avatar="👤"
            ):

                st.markdown(
                    message["content"]
                )


    # --------------------------------------------------------
    # QUICK QUESTIONS
    # --------------------------------------------------------

    st.caption(
        "Quick questions"
    )

    q1, q2 = st.columns(2)


    with q1:

        booking_help = st.button(
            "✈️ Booking help",
            use_container_width=True,
            key="assistant_booking"
        )


    with q2:

        payment_help = st.button(
            "💳 Payment help",
            use_container_width=True,
            key="assistant_payment"
        )


    # --------------------------------------------------------
    # BOOKING QUICK QUESTION
    # --------------------------------------------------------

    if booking_help:

        question = (
            "What should I do if I have a problem "
            "with my booking?"
        )

        st.session_state.assistant_messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        reply = get_assistant_response(
            question
        )

        st.session_state.assistant_messages.append(
            {
                "role": "assistant",
                "content": reply
            }
        )

        st.rerun()


    # --------------------------------------------------------
    # PAYMENT QUICK QUESTION
    # --------------------------------------------------------

    if payment_help:

        question = (
            "What should I do if money was deducted "
            "but I have a payment or booking problem?"
        )

        st.session_state.assistant_messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        reply = get_assistant_response(
            question
        )

        st.session_state.assistant_messages.append(
            {
                "role": "assistant",
                "content": reply
            }
        )

        st.rerun()


    # --------------------------------------------------------
    # ASSISTANT INPUT
    # --------------------------------------------------------

    with st.form(
        "assistant_form",
        clear_on_submit=True
    ):

        assistant_input = st.text_input(
            "Ask the AI Assistant",
            placeholder="Type your question..."
        )

        assistant_send = st.form_submit_button(
            "Send ➤",
            use_container_width=True
        )


    # --------------------------------------------------------
    # SEND ASSISTANT MESSAGE
    # --------------------------------------------------------

    if assistant_send:

        if assistant_input.strip():

            user_message = (
                assistant_input.strip()
            )

            st.session_state.assistant_messages.append(
                {
                    "role": "user",
                    "content": user_message
                }
            )

            reply = get_assistant_response(
                user_message
            )

            st.session_state.assistant_messages.append(
                {
                    "role": "assistant",
                    "content": reply
                }
            )

            st.rerun()


# ============================================================
# 19. FOOTER
# ============================================================

st.markdown(
    """
    <div style="
        text-align:center;
        padding:30px 0 10px 0;
        color:#786d80;
        font-size:12px;
    ">
        AI Helpdesk Ticket Router • Gemini API • AI Assistant
    </div>
    """,
    unsafe_allow_html=True
)