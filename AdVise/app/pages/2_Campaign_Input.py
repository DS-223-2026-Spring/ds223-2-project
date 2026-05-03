import streamlit as st
from ui_components import page_header, placeholder_box
from api_client import get_status, get_enums, submit_preview_prediction

st.set_page_config(page_title="Campaign Input", layout="wide")

page_header(
    "Campaign Input",
    "Upload creatives, enter campaign details, and prepare prediction request."
)

status, status_code = get_status()
enums = get_enums()

if status_code == 200:
    st.success("Backend connected. Ready to analyze campaigns.")
else:
    st.warning(
        "Backend is not connected yet. The form still works with fallback dropdown values."
    )

st.divider()

st.markdown("### Step 1 — Upload Creative Assets")

left, right = st.columns([1.1, 1.9], gap="large")

with left:
    uploaded_files = st.file_uploader(
        "Upload 1–3 creatives",
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg", "mp4"],
        help="Maximum creative count will later come from /v1/status."
    )

    if uploaded_files:
        if len(uploaded_files) > 3:
            st.error("Please upload maximum 3 creatives.")
        else:
            st.success(f"{len(uploaded_files)} creative(s) uploaded.")
    else:
        st.info("Upload campaign images or videos.")

with right:
    placeholder_box(
        "Creative Preview Area",
        "Uploaded creative previews and extracted features will appear here."
    )

st.divider()

st.markdown("### Step 2 — Campaign Details")

with st.container(border=True):
    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        campaign_name = st.text_input("Campaign Name")
        budget = st.number_input("Budget", min_value=0)
        platform = st.selectbox("Platform", enums["platforms"])

    with col2:
        campaign_intent = st.selectbox("Campaign Intent", enums["campaign_intents"])
        cta_type = st.selectbox("CTA Type", enums["cta_types"])
        audience_temperature = st.selectbox(
            "Audience Temperature",
            enums["audience_temperatures"]
        )

    with col3:
        duration = st.number_input("Duration in Days", min_value=1)
        device = st.selectbox("Device", enums["devices"])
        customer_type = st.selectbox("Customer Type", enums["customer_types"])

st.divider()

st.markdown("### Step 3 — Review Before Analysis")

with st.container(border=True):
    c1, c2, c3, c4 = st.columns(4, gap="large")

    with c1:
        st.metric("Platform", platform)
        st.metric("Intent", campaign_intent)

    with c2:
        st.metric("Budget", f"${budget}")
        st.metric("Duration", f"{duration} days")

    with c3:
        st.metric("Audience", audience_temperature)
        st.metric("CTA", cta_type)

    with c4:
        st.metric("Device", device)
        st.metric("Customer", customer_type)

st.divider()

st.subheader("Prepared Filter Area")

filter_col1, filter_col2, filter_col3 = st.columns(3, gap="large")

with filter_col1:
    st.selectbox("Preview Filter: Platform", ["All", platform])

with filter_col2:
    st.selectbox("Preview Filter: Audience", ["All", audience_temperature])

with filter_col3:
    st.selectbox("Preview Filter: Intent", ["All", campaign_intent])

st.divider()

st.subheader("Prepared Data Table Area")

st.dataframe(
    {
        "Field": [
            "Campaign Name",
            "Budget",
            "Platform",
            "Intent",
            "CTA Type",
            "Audience",
            "Duration",
            "Device",
            "Customer Type",
            "Uploaded Creatives",
        ],
        "Value": [
            campaign_name if campaign_name else "Not entered",
            f"${budget}",
            platform,
            campaign_intent,
            cta_type,
            audience_temperature,
            f"{duration} days",
            device,
            customer_type,
            len(uploaded_files) if uploaded_files else 0,
        ],
    },
    use_container_width=True,
)

st.divider()

analyze_clicked = st.button(
    "Analyze Campaign",
    use_container_width=True,
    type="primary"
)

if analyze_clicked:
    if not uploaded_files:
        st.error("Please upload at least one creative before analysis.")

    elif len(uploaded_files) > 3:
        st.error("Please upload no more than 3 creatives.")

    elif campaign_name.strip() == "":
        st.error("Please enter a campaign name.")

    else:
        payload = {
            "campaign_name": campaign_name,
            "budget": budget,
            "platform": platform,
            "campaign_intent": campaign_intent,
            "cta_type": cta_type,
            "audience_temperature": audience_temperature,
            "duration": duration,
            "device": device,
            "customer_type": customer_type,
        }

        files = [
            (
                "files",
                (
                    file.name,
                    file.getvalue(),
                    file.type,
                ),
            )
            for file in uploaded_files
        ]

        with st.status("Processing campaign prediction...", expanded=True):
            st.write("Validating campaign payload.")
            st.write("Preparing creative files.")
            st.write("Waiting for backend prediction response.")

            result, response_code = submit_preview_prediction(payload, files)

        if response_code == 200 and result:
            st.session_state["prediction_result"] = result
            st.session_state["campaign_payload"] = payload
            st.success("Prediction completed. Open the Prediction Results page.")

        else:
            st.session_state["campaign_payload"] = payload
            st.session_state["prediction_result"] = {
                "best_creative": "Creative A",
                "primary_kpi": "Predicted CTR",
                "creatives": [
                    {
                        "name": "Creative A",
                        "rank": 1,
                        "ctr": "2.8%",
                        "conversion_rate": "3.9%",
                        "engagement_score": 86,
                        "recommendation": "Best option because CTA and message are clear."
                    },
                    {
                        "name": "Creative B",
                        "rank": 2,
                        "ctr": "2.3%",
                        "conversion_rate": "3.4%",
                        "engagement_score": 79,
                        "recommendation": "Good alternative, but CTA visibility can improve."
                    },
                    {
                        "name": "Creative C",
                        "rank": 3,
                        "ctr": "1.9%",
                        "conversion_rate": "2.7%",
                        "engagement_score": 71,
                        "recommendation": "Needs improvement because text density is high."
                    },
                ],
                "tips": [
                    "Launch with the highest ranked creative.",
                    "Improve CTA visibility before publishing.",
                    "Keep message short and aligned with campaign intent.",
                    "Use prediction results as pre-launch guidance, not final truth."
                ]
            }

            st.warning(
                "Backend response was not available, so placeholder prediction results were prepared for frontend flow testing."
            )
            st.success("Open the Prediction Results page to view the result layout.")