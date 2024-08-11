from typing import Literal, Optional
from langchain_core.tools import tool
import plotly.graph_objs as go
import json

@tool
def plot_chart(
    data: str,
    plot_title: str,
    x_label: str,
    y_label: str,
    plot_type: Literal["bar", "line", "scatter"] = "line",
    save_path: Optional[str] = "./tmp.png",
    template: Literal["plotly"] = "plotly"
) -> str:
    """
    Generate a bar chart, line chart, or scatter plot based on input data using Plotly.
    
    WARNING:This function can only be used when both the x and y axes are arrays of the same length. Elements cannot be set as a tuple.

    Parameters:
    data (str): A JSON string containing 'x_values' and 'y_values' lists.
    plot_title (str): Title of the plot.
    x_label (str): Label for the x-axis.
    y_label (str): Label for the y-axis.
    plot_type (str, optional): Type of plot to generate. Options are "bar", "line", or "scatter". Default is "line".
    save_path (str, optional): Path to save the plot image locally. If None, the plot image will not be saved. Default is "./tmp.png".
    template (str, optional): Plotly template to use. Default is "plotly".

    Returns:
    str: A string representation of the Plotly Figure object.

    Raises:
    ValueError: If the lengths of x_values and y_values are not the same or if there's an error parsing the input.

    Example:
    data = '{"x_values": [1, 2, 3, 4, 5], "y_values": [2, 4, 1, 5, 3]}'
    plot_chart(data, "Sample Chart", "X Axis", "Y Axis", "line")
    """
    try:
        # Parse the JSON string
        data_dict = json.loads(data)
        x_values = data_dict['x_values']
        y_values = data_dict['y_values']
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON string provided for 'data'")
    except KeyError:
        raise ValueError("The 'data' JSON must contain 'x_values' and 'y_values' keys")

    # Validate input lengths
    if len(x_values) != len(y_values):
        raise ValueError("Lengths of x_values and y_values must be the same.")


    # Define plotly trace based on plot_type
    if plot_type == 'bar':
        trace = go.Bar(
            x=x_values, 
            y=y_values, 
            marker=dict(color='#24C8BF', line=dict(width=1))
        )
    elif plot_type == 'scatter':
        trace = go.Scatter(
            x=x_values, 
            y=y_values, 
            mode='markers', 
            marker=dict(color='#df84ff', size=10, opacity=0.7, line=dict(width=1))
        )
    else:  # Default to 'line'
        trace = go.Scatter(
            x=x_values, 
            y=y_values, 
            mode='lines+markers', 
            marker=dict(color='#ff9900', size=8, line=dict(width=1)), 
            line=dict(width=2, color='#ff9900')
        )

    # Create layout for the plot
    layout = go.Layout(
        title=f'{plot_title} {plot_type.capitalize()} Chart',
        title_font=dict(size=20, family='Arial', color='#333'),
        xaxis=dict(
            title=x_label, 
            titlefont=dict(size=18), 
            tickfont=dict(size=14), 
            gridcolor='#f0f0f0'
        ),
        yaxis=dict(
            title=y_label, 
            titlefont=dict(size=18), 
            tickfont=dict(size=14), 
            gridcolor='#f0f0f0'
        ),
        margin=dict(l=60, r=60, t=80, b=60),
        plot_bgcolor='#f8f8f8',
        paper_bgcolor='#f8f8f8',
        template=template
    )

    # Create the figure
    fig = go.Figure(data=[trace], layout=layout)
    
    # Optionally save the figure
    if save_path:
        fig.write_image(save_path)

    return str(fig)