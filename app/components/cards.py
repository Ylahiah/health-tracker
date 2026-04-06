import streamlit as st

def metric_card(label, value, delta=None, help_text=None):
    """
    Displays a metric card using st.metric.
    """
    st.metric(label=label, value=value, delta=delta, help=help_text)

def progress_card(label, value, max_value, unit=""):
    """
    Displays a progress bar with a label.
    """
    st.write(f"**{label}**")
    progress = min(max(value / max_value, 0.0), 1.0)
    st.progress(progress)
    st.caption(f"{value} / {max_value} {unit}")
