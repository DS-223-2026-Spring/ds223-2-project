import base64
import streamlit as st
from ui_components import page_header, placeholder_box
from api_client import get_status, get_enums, submit_preview_prediction, create_campaign

st.set_page_config(page_title="Campaign Input — AdVise", layout="wide")
inject_global_css()

page_header(
    "Campaign Input",
    "Upload creatives, enter campaign details, and prepare the prediction request.",
)

status, status_code = get_status()
enums = get_enums()

if status_code == 200:
    st.success("✓ Backend connected — ready to analyze campaigns.")
else:
    st.warning("Backend not reachable — form works with fallback dropdown values.")

# ── Step 1: Creative Upload ───────────────────────────────────────────────────
st.markdown("### Step 1 — Upload Creative Assets")

left, right = st.columns([1.1, 1.9], gap="large")

with left:
    uploaded_files = st.file_uploader(
        "Upload 1–3 creatives",
        accept_multiple_files=True,
        type=["png", "jpg", "jpeg", "mp4"],
        help="Maximum creative count will later come from /v1/status.",
    )
    if uploaded_files:
        if len(uploaded_files) > 3:
            st.error("Please upload maximum 3 creatives.")
        else:
            st.success(f"{len(uploaded_files)} creative(s) uploaded.")
    else:
        st.info("Upload campaign images or videos.")

with right:
    st.subheader("Creative preview")
    prev_result = st.session_state.get("prediction_result")

    if uploaded_files:
        first = uploaded_files[0]
        if first.type and first.type.startswith("image/"):
            st.image(first.getvalue(), caption="First creative (sent to API as base64)")
        else:
            st.info("First file is not an image — pixel extraction skipped until video support lands.")
    else:
        st.caption("Upload an image to see a preview here.")

    feats = prev_result.get("creative_features") if isinstance(prev_result, dict) else None
    if feats:
        with st.expander("Last run: extracted creative features", expanded=True):
            st.json(feats)
    else:
        placeholder_box(
            "Extracted features",
            "After **Analyze Campaign**, image extraction results appear here when the API's creative extraction runs.",
        )

st.divider()

# ── Step 2: Campaign Details ──────────────────────────────────────────────────
st.markdown("### Step 2 — Campaign Details")

with st.container(border=True):
    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        campaign_name = st.text_input("Campaign Name")
        budget        = st.number_input("Budget ($)", min_value=0)
        platform      = st.selectbox("Platform", enums["platforms"])

    with col2:
        campaign_intent      = st.selectbox("Campaign Intent", enums["campaign_intents"])
        cta_type             = st.selectbox("CTA Type", enums["cta_types"])
        audience_temperature = st.selectbox("Audience Temperature", enums["audience_temperature"])
        product_type         = st.selectbox("Product Type", enums.get("product_types", ["software"]))

    with col3:
        duration      = st.number_input("Duration (days)", min_value=1)
        device        = st.selectbox("Device", enums["devices"])
        customer_type = st.selectbox("Customer Type", enums["customer_types"])

st.divider()

# ── Step 3: Review ───────────────────────────────────────────────────────────
st.markdown("### Step 3 — Review Before Analysis")

with st.container(border=True):
    c1, c2, c3, c4 = st.columns(4, gap="large")
    with c1:
        st.metric("Platform", platform)
        st.metric("Intent", campaign_intent)
    with c2:
        st.metric("Budget", f"${budget:,.0f}")
        st.metric("Duration", f"{duration} days")
    with c3:
        st.metric("Audience", audience_temperature)
        st.metric("CTA", cta_type)
    with c4:
        st.metric("Device", device)
        st.metric("Customer", customer_type)

st.divider()

# ── Analyze button ────────────────────────────────────────────────────────────
analyze_clicked = st.button("Analyze Campaign", use_container_width=True, type="primary")

if analyze_clicked:
    if not uploaded_files:
        st.error("Please upload at least one creative before analysis.")
    elif len(uploaded_files) > 3:
        st.error("Please upload no more than 3 creatives.")
    elif not campaign_name.strip():
        st.error("Please enter a campaign name.")
    else:
        payload: dict = {
            "platform":             platform,
            "campaign_intent":      campaign_intent,
            "product_type":         product_type,
            "cta_type":             cta_type,
            "audience_temperature": audience_temperature,
            "customer_type":        customer_type,
            "budget":               float(budget),
            "duration_days":        int(duration),
            "creative_count":       min(3, len(uploaded_files)),
        }

        campaign_save_payload = {
            "company": campaign_name,
            "campaign_type": campaign_intent,
            "platform": platform,
            "budget": float(budget),
            "duration_days": int(duration),
            "campaign_intent": campaign_intent,
            "product_type": product_type,
        }

        first = uploaded_files[0]
        if first.type and first.type.startswith("image/"):
            payload["creative_image_base64"] = base64.standard_b64encode(
                first.getvalue()
            ).decode("ascii")

        with st.status("Processing campaign prediction...", expanded=True):
            st.write("Saving campaign configuration to PostgreSQL.")

            saved_campaign = create_campaign(campaign_save_payload)

            if "error" in saved_campaign:
                st.warning(f"Campaign was not saved to DB: {saved_campaign['error']}")
            else:
                st.success(f"Campaign saved to DB with ID {saved_campaign['campaign_id']}.")

            st.write("Validating campaign payload for /v1/predictions/preview (JSON).")

            if "creative_image_base64" in payload:
                st.write("Sending first image as base64 → API runs creative feature extraction.")
            else:
                st.write("Video / non-image creative: skipping pixel extraction.")

            st.write("Waiting for backend prediction response.")

            result, response_code = submit_preview_prediction(payload)

        if response_code == 200 and result:
            st.session_state["prediction_result"] = result
            st.session_state["campaign_payload"]  = payload
            st.success("✓ Prediction completed. Open **Prediction Results** in the sidebar.")
        else:
            # Fallback placeholder so the Results page still renders
            st.session_state["campaign_payload"]  = payload
            st.session_state["prediction_result"] = {
                "best_creative": "Creative A",
                "primary_kpi":   "Predicted CTR",
                "creatives": [
                    {
                        "name": "Creative A", "rank": 1, "ctr": "2.8%",
                        "conversion_rate": "3.9%", "engagement_score": 86,
                        "recommendation": "Best option — CTA and message are clear.",
                    },
                    {
                        "name": "Creative B", "rank": 2, "ctr": "2.3%",
                        "conversion_rate": "3.4%", "engagement_score": 79,
                        "recommendation": "Good alternative — CTA visibility can improve.",
                    },
                    {
                        "name": "Creative C", "rank": 3, "ctr": "1.9%",
                        "conversion_rate": "2.7%", "engagement_score": 71,
                        "recommendation": "Needs improvement — text density is high.",
                    },
                ],
                "tips": [
                    "Launch with the highest ranked creative.",
                    "Improve CTA visibility before publishing.",
                    "Keep message short and aligned with campaign intent.",
                    "Use prediction results as pre-launch guidance, not final truth.",
                ],
            }
            st.warning(
                "Backend not reachable — placeholder results prepared for frontend flow testing."
            )
            st.success("Open **Prediction Results** in the sidebar to view the result layout.")