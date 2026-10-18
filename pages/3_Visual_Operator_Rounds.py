import os
import streamlit as st
import requests
from PIL import Image
from ui_shared import apply_theme, module_header

API_URL = os.getenv("VISION_API_URL", "http://127.0.0.1:8003/vision/nameplate")

st.set_page_config(
    page_title="Visual Operator Rounds Assistant",
    layout="wide"
)

apply_theme()
module_header(
    "Module 03 · Computer Vision / OCR",
    "Visual Operator Rounds Assistant",
    "Upload an industrial equipment nameplate image and convert visual information into structured equipment intelligence using image preprocessing and OCR.",
)

uploaded_file = st.file_uploader(
    "Upload nameplate image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:

    image = Image.open(uploaded_file)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Uploaded Image")

        st.image(
            image,
            use_container_width=True
        )

    analyze_clicked = st.button(
        "Analyze Nameplate"
    )

    if analyze_clicked:

        try:

            with st.spinner(
                "Running computer vision analysis..."
            ):

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type
                    )
                }

                response = requests.post(
                    API_URL,
                    files=files,
                    timeout=120
                )

            if response.status_code == 200:

                result = response.json()

                with col2:

                    st.subheader(
                        "Extracted Information"
                    )

                    st.metric(
                        "Equipment Type",
                        result.get(
                            "equipment_type",
                            "Not detected"
                        )
                    )

                    st.metric(
                        "Manufacturer",
                        result.get(
                            "manufacturer",
                            "Not detected"
                        )
                    )

                    st.subheader(
                        "Detected Text"
                    )

                    raw_text = result.get(
                        "raw_text",
                        ""
                    )

                    if raw_text:
                        st.write(raw_text)
                    else:
                        st.info(
                            "No OCR text detected."
                        )

                    st.subheader(
                        "OCR Regions"
                    )

                    regions = result.get(
                        "detected_regions",
                        []
                    )

                    if regions:

                        for item in regions:

                            text = item.get(
                                "text",
                                ""
                            )

                            confidence = item.get(
                                "confidence",
                                0
                            )

                            st.write(
                                f"{text} "
                                f"(confidence: "
                                f"{confidence:.2f})"
                            )

                    else:

                        st.info(
                            "No OCR regions detected."
                        )

            else:

                st.error(
                    f"Vision API failed. "
                    f"Status code: "
                    f"{response.status_code}"
                )

                st.code(
                    response.text
                )

        except requests.exceptions.ConnectionError:

            st.error(
                "Cannot connect to the FastAPI backend. "
                "Make sure the Visual Operator Rounds API is running on port 8003."
            )

        except requests.exceptions.Timeout:

            st.error(
                "The analysis took too long and timed out."
            )

        except Exception as e:

            st.error(
                "Unexpected frontend error:"
            )

            st.code(
                str(e)
            )


st.divider()

with st.expander(
    "How this vision module works"
):

    st.markdown(
        """
        **Processing flow**

        1. User uploads an equipment nameplate image.
        2. Streamlit sends the image to FastAPI.
        3. OpenCV preprocesses the image.
        4. EasyOCR detects text regions and extracts text.
        5. Business logic identifies equipment information.
        6. FastAPI returns structured results.
        7. Streamlit displays the result.

        Low-confidence information is not invented.
        """
    )