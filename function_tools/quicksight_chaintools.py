from langchain_core.tools import tool
from utils.quicksight_assets_class import *
from typing import List, Dict, Union,Optional, TypedDict,Any
import json, datetime
from utils.bedrock_clients import client_qs

quicksight_builders = {}
@tool
def create_or_select_quicksight_builder_with_analysis(analysis_id,analysis_name,datasets,operate_type):
    """
    Create or select a QuickSight builder instance and initialize an analysis with datasets.
    
    Description: 
        Please first use the function('get_all_datasets_from_quicksight') to retrieve all data sources in quicksight syetem, and use function('get_table_info') to retrieve all the data and scheam in the database.
        Then this is a first step to use this function to create a new QuickSight builder and initialize an analysis. 

    Args:
        analysis_id (str): The ID for the new analysis.
        analysis_name (str): The name of the new analysis.
        datasets (List[Dict]): A list of dataset configurations, which selected by 'get_all_datasets_from_quicksight' function.
        operate_type (str): Must be one of: "SELECT" or "CREATE". "CREATE" is default.

    Returns:
        str: A message indicating the result and the builder_id for further operations.

    Note:
    - This function is the first step in creating a QuickSight analysis.
    - Make sure to use valid AWS account ID and unique analysis ID.
    - Dataset configurations should include both ARN and identifier.

    Example Input:
    analysis_id = ""
    analysis_name = ""
    operate_type = ""
    datasets = [
        {"dataset_arn": "", "dataset_identifier": ""}, 
        {"dataset_arn": "", "dataset_identifier": ""}
    ]
    """
    aws_account_id = '' 
    try:
        builder_id = str(analysis_id) + str(aws_account_id)
        builder = QuickSightBuilder(aws_account_id, analysis_id)
        builder.create_analysis(analysis_id, analysis_name, type=operate_type)
        for dataset in datasets:
            builder.add_dataset(dataset['dataset_arn'], dataset['dataset_identifier'])
        
        quicksight_builders[builder_id] = builder
        return f"Builder created with ID: {builder_id}. Use this ID for further operations."
    except Exception as e:
        return f"Error creating QuickSight builder: {str(e)}. Please check your inputs and try again."

@tool
def create_or_select_sheet(builder_id, sheet_id,sheet_name):
    """
    Select an existing sheet or create a new one if it doesn't exist.
    
    Description: 
        In the QuickSight hierarchy, an analysis contains multiple sheets, each of which can host various visuals, and the current step is to select an existing sheet or create a new one within your analysis
        The overall structure (analysis > sheets > visuals)
    Args:
        builder_id (str): The ID of the QuickSight builder.
        sheet_id (str): The ID for the sheet.
        sheet_name (str): The name of the sheet.

    Returns:
        str: A message indicating the result and the sheet_id for further operations.

    Note:
    - This function should be called after creating the QuickSight builder.
    - If the sheet doesn't exist, it will be created with a grid layout.
    - Use the returned sheet_id for adding visuals or filter controls.

    Example Input:
    builder_id = ""
    sheet_id = ""
    sheet_name = ""
    """
    builder = quicksight_builders.get(builder_id)
    if not builder:
        return f"Error: Builder with ID {builder_id} not found."
    
    if sheet_id not in builder.sheets:
        builder.create_sheet(sheet_id, sheet_name)
        builder.set_sheet_layout(sheet_id, "GRID")
        return f"Sheet '{sheet_name}' (ID: {sheet_id}) created. Use this sheet_id for adding visuals or filter controls."
    else:
        return f"Existing sheet '{sheet_name}' (ID: {sheet_id}) selected. Use this sheet_id for adding visuals or filter controls."


@tool
def create_or_operate_charts(
    builder_id: str,
    sheet_id: str,
    visual_configs: List[Dict[str, Union[str, int, List[str], List[int], Optional[str], Optional[List[str]]]]]
) -> str:
    """
    Create or operate on charts based on the provided configurations.
    After creating or selecting a sheet by select_or_create_sheet function, execute the current function to add or modify charts/visuals for it.
    
    Description: 
        In the QuickSight hierarchy, an analysis contains multiple sheets, each of which can host various charts(visuals), and the current step is to update an existing chart or create a new one within your sheet
        The overall structure (analysis > sheets > charts/visuals)
    Args:
        builder_id (str): The ID of the QuickSight builder.
        sheet_id (str): The ID of the sheet to add visuals to.
        visual_configs (List[Dict]): A list of visual configurations. The structure depends on the visual type.

    Returns:
        str: A message indicating the result of the operations, including the number and IDs of created visuals.

    Note:
    - This function supports creating BAR, LINE, PIE, and TABLE charts.
    - Each visual configuration should include all necessary parameters for the specific chart type.
    - The function handles two different configuration structures based on the visual type.
    - After creating visuals, you can proceed to add filters and controls or finalize the analysis.

    For BAR, LINE, and PIE charts, each dictionary in visual_configs should have the following structure:
    {
        "visual_id": str,  # A unique identifier for the visual
        "visual_type": str,  # Must be one of: "BAR", "LINE", "PIE"
        "title": str,  # The title of the visual
        "x_position": int,  # The x-position of the visual on the sheet (0-based)
        "y_position": int,  # The y-position of the visual on the sheet (0-based)
        "width": int,  # The width of the visual (1-24, representing grid units)
        "height": int,  # The height of the visual (in grid units)
        "x_field": str,  # The name of the field for the X-axis (must match the original column name in SQL)
        "x_field_type": str,  # Must be one of: "DIMENSION", "DATE", "MEASURE"
        "x_dataset_identifier": str,  # The dataset identifier for the X-axis field (must match the table name in SQL)
        "y_field": str,  # The name of the field for the Y-axis (must match the original column name in SQL)
        "y_field_type": str,  # Must be one of: "MEASURE", "DATE" (cannot be "DIMENSION")
        "y_dataset_identifier": str,  # The dataset identifier for the Y-axis field (must match the table name in SQL)
        "color_field": Optional[str],  # The name of the field for color (optional, must match the original column name in SQL)
        "color_field_type": Optional[str],  # Must be one of: "DIMENSION", "DATE", "MEASURE" (if color_field is provided)
        "color_dataset_identifier": Optional[str],  # The dataset identifier for the color field (if provided, must match the table name in SQL)
        "x_date_granularity": Optional[str],  # Required if x_field_type is "DATE". E.g., "YEAR", "QUARTER", "MONTH", "WEEK", "DAY"
        "y_aggregation_function": Optional[str],  # Required if y_field_type is "MEASURE". E.g., "SUM", "AVERAGE", "MIN", "MAX", "COUNT", "VAR", "VARP", "MEDIAN", "DISTINCT_COUNT", "STDEV", "STDEVP"
        "color_date_granularity": Optional[str],  # Required if color_field_type is "DATE". E.g., "YEAR", "QUARTER", "MONTH", "WEEK", "DAY"
    }

    For TABLE charts, each dictionary in visual_configs should have the following structure:
    {
        "visual_id": str,  # A unique identifier for the visual
        "visual_type": str,  # Must be "TABLE"
        "title": str,  # The title of the visual
        "x_position": int,  # The x-position of the visual on the sheet (0-based)
        "y_position": int,  # The y-position of the visual on the sheet (0-based)
        "width": int,  # The width of the visual (1-24, representing grid units)
        "height": int,  # The height of the visual (in grid units)
        "x_fields": List[str],  # List of field names for the table columns (must match the original column names in SQL)
        "x_field_types": List[str],  # List of field types corresponding to x_fields. Each must be one of: "DIMENSION", "DATE", "MEASURE"
        "x_dataset_identifier": str,  # The dataset identifier for the X-axis fields (must match the table name in SQL)
        "y_fields": List[str],  # List of field names for the table values (must match the original column names in SQL)
        "y_field_types": List[str],  # List of field types corresponding to y_fields. Each must be one of: "MEASURE", "DATE"
        "y_dataset_identifier": str,  # The dataset identifier for the Y-axis fields (must match the table name in SQL)
        "x_date_granularity": Optional[str],  # Required if any x_field_type is "DATE". E.g., "YEAR", "QUARTER", "MONTH", "WEEK", "DAY"
        "y_aggregation_function": Optional[str],  # Required if any y_field_type is "MEASURE". E.g., "SUM", "AVERAGE", "MIN", "MAX", "COUNT", "VAR", "VARP", "MEDIAN", "DISTINCT_COUNT", "STDEV", "STDEVP"
    }

    Important notes:
    - The function will raise a ValueError if any input parameters are invalid.
    - For BAR, LINE, and PIE charts, y_field_type cannot be "DIMENSION".
    - Each visual can have at most one category type (DIMENSION or DATE used as a dimension) across x_field and color_field.
    - The color_field is optional for BAR, LINE, and PIE charts and can be used for additional grouping or segmentation.
    - Always specify date granularity for DATE fields and aggregation functions for MEASURE fields.
    - For TABLE charts, x_fields represent the table columns, and y_fields represent the table values.
    - The function sets the visual title, adds it to the sheet, and configures its layout after creation.

    Example usage:
    operate_or_create_charts(
        "builder_123",
        "sheet_1",
        [
            {
                "visual_id": "",
                "visual_type": "",
                "title": "",
                "x_position": ,
                "y_position": ,
                "width": ,
                "height": ,
                "x_field": "",
                "x_field_type": "",
                "x_dataset_identifier": "",
                "x_date_granularity": "",
                "y_field": "",
                "y_field_type": "",
                "y_dataset_identifier": "",
                "y_aggregation_function": "",
                "color_field": "",
                "color_field_type": "",
                "color_dataset_identifier": ""
            },
            {
                "visual_id": "",
                "visual_type": "",
                "title": "",
                "x_position": ,
                "y_position": ,
                "width": ,
                "height": ,
                "x_fields": ["", "", ""],
                "x_field_types": ["", "", ""],
                "x_dataset_identifier": "",
                "y_fields": ["", ""],
                "y_field_types": ["", ""],
                "y_dataset_identifier": "",
                "x_date_granularity": "",
                "y_aggregation_function": ""
            }
        ]
    )
    """
    try:
        builder = quicksight_builders.get(builder_id)
        if not builder:
            return f"Error: Builder with ID {builder_id} not found."
        
        created_visuals = []
        for config in visual_configs:
            try:
                if config['visual_type'] in ['BAR', 'LINE', 'PIE']:
                    builder.create_or_operate_line_bar_visual(
                        sheet_id=sheet_id,
                        visual_type=config['visual_type'],
                        visual_id=config['visual_id'],
                        title=config['title'],
                        x_field=config['x_field'],
                        x_field_type=config['x_field_type'],
                        x_dataset_identifier=config['x_dataset_identifier'],
                        y_field=config['y_field'],
                        y_field_type=config['y_field_type'],
                        y_dataset_identifier=config['y_dataset_identifier'],
                        color_field=config.get('color_field'),
                        color_field_type=config.get('color_field_type'),
                        color_dataset_identifier=config.get('color_dataset_identifier'),
                        x_date_granularity=config.get('x_date_granularity'),
                        y_aggregation_function=config.get('y_aggregation_function'),
                        color_date_granularity=config.get('color_date_granularity')
                    )
                elif config['visual_type'] in ['TABLE']:
                    builder.create_or_operate_table_visual(
                        sheet_id=sheet_id,
                        visual_id=config['visual_id'],
                        x_fields=config['x_fields'],
                        x_field_types=config['x_field_types'],
                        x_dataset_identifier=config['x_dataset_identifier'],
                        y_fields=config['y_fields'],
                        y_field_types=config['y_field_types'],
                        y_dataset_identifier=config['y_dataset_identifier'],
                        x_date_granularity=config.get('x_date_granularity'),
                        y_aggregation_function=config.get('y_aggregation_function')
                    )
                else:
                    raise ValueError(f"Unsupported visual type '{config['visual_type']}' for visual '{config['visual_id']}'.")

                builder.set_visual_title(config['visual_id'], config['title'])
                builder.add_visual_to_sheet(sheet_id, config['visual_id'])
                builder.add_visual_layout_to_sheet(
                    sheet_id,
                    config['visual_id'],
                    int(config['x_position']),
                    int(config['y_position']),
                    int(config['width']),
                    int(config['height'])
                )
                created_visuals.append(config['visual_id'])
            except Exception as e:
                return f"Error creating visual {config['visual_id']}: {str(e)}. Skipping this visual."

        return f"Created and added {len(created_visuals)} visuals to sheet {sheet_id}: {', '.join(created_visuals)}. You can now add filters and controls or finalize the analysis."
    except Exception as e:
        return f"Error in operate_or_create_charts: {str(e)}. Please check your inputs and try again."

@tool
def create_or_operate_filter_and_control(
    builder_id: str,
    sheet_id: str,
    filter_configs: List[Dict[str, Union[str, Dict]]],
    filter_control_configs: List[Dict[str, Union[str, Dict]]],
    filter_group_configs: List[Dict[str, Union[str, List[str]]]]
) -> str:
    """
    Create or operate on filters, filter controls, and filter groups based on the provided configurations.
    After selecting visuals or executing operate_or_create_charts function, use this function to add/update filters and filter controls to your analysis.
    
    Description: 
        In the QuickSight hierarchy, an analysis contains multiple sheets, each of which can host various charts(visuals).
        This step is to update existing filters and filter controls or create new ones within your sheet.
        The overall structure is (analysis > sheets > charts). The filter control is operated at the sheet level.

    Args:
        builder_id (str): The ID of the QuickSight builder.
        sheet_id (str): The ID of the sheet to add filter controls to.
        filter_configs (List[Dict]): A list of filter configurations.
        filter_control_configs (List[Dict]): A list of filter control configurations.
        filter_group_configs (List[Dict]): A list of filter group configurations.

    Returns:
        str: A message indicating the result of the operations.

    Note:
    - This function should be called after creating visuals.
    - Ensure that the filter_configs and filter_control_configs match your visual configurations.
    - IMPORTANT: All filters within a single filter group MUST come from the same dataset.
      It is the user's responsibility to ensure that the filter_ids in each group correspond
      to filters from the same dataset.
      filter_type MUST be one of 'CategoryFilter' or 'TimeRangeFilter'
      control_type MUST be one of 'DateTimePicker' or 'Dropdown'

    Example Input:
    builder_id = ""
    sheet_id = ""
    filter_configs = [
        {
            "filter_id": "",
            "column_name": "",
            "data_set_identifier": "",
            "filter_type": "", # filter_type must be one of 'CategoryFilter' or 'TimeRangeFilter'
            "configuration":{"null_option":"ALL_VALUES"} #for the TimeRangeFilter filter type, this is the default configuration
        },
        {
            "filter_id": "",
            "column_name": "",
            "data_set_identifier": "",
            "filter_type": "", # filter_type must be one of 'CategoryFilter' or 'TimeRangeFilter'
            "configuration": { #for the CategoryFilter filter type, this is the default configuration
                "match_operator": "CONTAINS",
            }
        }
    ]
    filter_control_configs = [
        {
            "filter_control_id": "",
            "source_filter_id": "",
            "title": "",
            "control_type": "", #control_type MUST be one of 'DateTimePicker' or 'Dropdown'
            "configuration": { #for the DateTimePicker control type, this is the default configuration
                "date_time_format": "YYYY-MM-DD",
                "type": "DATE_RANGE" 
            },
            "layout": {
                "column_span": 2,
                "row_span": 1
            }
        },
        {
            "filter_control_id": "",
            "source_filter_id": "",
            "title": "",
            "control_type": "", #control_type MUST be one of 'DateTimePicker' or 'Dropdown'
            "configuration": { # for the Dropdown control type, this is the default configuration
                "type": "MULTI_SELECT",
                "display_options": {
                    "select_all_options": {
                        "visibility": "VISIBLE"
                    }
                }
            },
            "layout": {
                "column_span": 2,
                "row_span": 1
            }
        }
    ]
    filter_group_configs = [
        {
            "group_id": "",
            "dataset_identifier": "",
            "filter_ids": ["", ""]
        }
    ]
    """
    builder = quicksight_builders.get(builder_id)
    if not builder:
        return f"Error: Builder with ID {builder_id} not found."

    created_filters = []
    created_controls = []
    created_groups = []

    # Create filters
    for filter_config in filter_configs:
        builder.create_filter(
            filter_id=filter_config['filter_id'],
            column_name=filter_config['column_name'],
            data_set_identifier=filter_config['data_set_identifier'],
            filter_type=filter_config['filter_type'],
            **filter_config['configuration']
        )
        created_filters.append(filter_config['filter_id'])

    # Create filter controls
    builder.set_sheet_control_layout(sheet_id)
    for control_config in filter_control_configs:
        builder.create_filter_control(
            filter_control_id=control_config['filter_control_id'],
            source_filter_id=control_config['source_filter_id'],
            title=control_config['title'],
            control_type=control_config['control_type'],
            **control_config['configuration']
        )
        builder.add_filter_control_to_sheet(sheet_id, control_config['filter_control_id'])
        builder.add_filter_control_to_layout(
            sheet_id,
            control_config['filter_control_id'],
            control_config['layout']['column_span'],
            control_config['layout']['row_span']
        )
        created_controls.append(control_config['filter_control_id'])

    # Create filter groups
    for group_config in filter_group_configs:
        try:
            builder.create_filter_group(group_config['group_id'], group_config['dataset_identifier'])
            builder.add_filter_to_group(group_config['group_id'], group_config['filter_ids'])
            created_groups.append(group_config['group_id'])
        except ValueError as e:
            return f"Error creating or configuring filter group {group_config['group_id']}: {str(e)}"

    #builder.add_filter_groups_to_definition()

    return f"Created {len(created_filters)} filters, {len(created_controls)} filter controls, and {len(created_groups)} filter groups. " \
           f"Filters: {', '.join(created_filters)}. Controls: {', '.join(created_controls)}. Groups: {', '.join(created_groups)}. " \
           f"You can now finalize the analysis."
@tool
def build_compile(builder_id: str) -> str:
    """
    Finalize and compile the QuickSight analysis.
    "This is the final step in creating your QuickSight analysis. Use this function to compile "
    "all the configurations and create the analysis in AWS QuickSight. You only need to provide "
    Args:
        builder_id (str): The ID of the QuickSight builder.

    Returns:
        str: A message indicating the result of the compilation and creation process.

    Note:
    - This is the final step in creating a QuickSight analysis.
    - It compiles all the configurations and creates the analysis in AWS QuickSight.
    - If successful, it returns the ARN of the created analysis.

    Example Input:
    builder_id = ""
    """
    try:
        builder = quicksight_builders.get(builder_id)
        if not builder:
            return f"Error: Builder with ID {builder_id} not found."

        builder.add_sheets_to_analysis()
        builder.add_filter_groups_to_definition()
        analysis_json = builder.build()
        file = json.dumps(analysis_json, indent=6)
        with open("analysis_json.json", "w") as outfile:
            outfile.write(file)
        try:
            response = client_qs.create_analysis(**analysis_json)
            return f"Analysis successfully created. Analysis ARN: {response['Arn']}. You can now view the analysis in QuickSight."
        except Exception as e:
            return f"Error occurred while creating the analysis in QuickSight: {str(e)}. Please check your QuickSight configuration and try again."
    except Exception as e:
        return f"Error in build_compile: {str(e)}. Please check your inputs and try again."
#====================================================================
# QuickSightBuilder Class:
# This class is used to balance the trivial property configuration with the functional tasks of platform roles.
#====================================================================
class QuickSightBuilder:
    def __init__(self, aws_account_id,analysis_id):
        self.builder_id = str(analysis_id+aws_account_id)
        self.aws_account_id = ''
        self.analysis = None
        self.definition = None
        self.sheets = {}
        self.visuals = {}
        self.dataset_map = {}
        self.filters = {}
        self.filter_controls = {}
        self.filter_groups = {} 

    def create_analysis(self, analysis_id: str, analysis_name: str, type='CREATE'):
        self.analysis = Analysis(self.aws_account_id, analysis_id, analysis_name)
        if type=='CREATE':
            self.analysis.add_permission(
                  actions=["quicksight:RestoreAnalysis", "quicksight:UpdateAnalysisPermissions", "quicksight:DeleteAnalysis", 
                        "quicksight:QueryAnalysis", "quicksight:DescribeAnalysisPermissions", "quicksight:DescribeAnalysis", 
                        "quicksight:UpdateAnalysis"],
                  principal=""
            )
        return self

    def add_dataset(self, dataset_arn: str, dataset_identifier: str):
        if not self.analysis:
            raise ValueError("Analysis must be created first")
        
        if not self.definition:
            self.definition = Definition([])
        
        self.definition.data_set_definition.append({"DataSetArn": dataset_arn, "Identifier": dataset_identifier})
        self.dataset_map[dataset_arn] = dataset_identifier
        self.definition.set_analysis_default()
        return self

    def create_sheet(self, sheet_id: str, sheet_name: str):
        if not self.definition:
            raise ValueError("Definition must be created first")
        if sheet_id not in self.sheets:
            self.sheets[sheet_id] = Sheet(sheet_id, sheet_name)
        return self

    def set_sheet_layout(self, sheet_id: str, layout_type: str, width: str = "1600px"):
        if sheet_id not in self.sheets:
            raise ValueError(f"Sheet {sheet_id} does not exist")
        
        if layout_type == "GRID":
            self.sheets[sheet_id].set_grid_layout("FIXED", width)
        elif layout_type == "FREE_FORM":
            self.sheets[sheet_id].set_freeform_layout()
        return self

    def create_filter(self, filter_id: str, column_name: str, data_set_identifier: str, filter_type: str, **kwargs):
        if filter_type == "CategoryFilter":
            new_filter = CategoryFilter(filter_id, column_name, data_set_identifier)
            new_filter.add_filter_list_configuration(**kwargs)
        elif filter_type == "TimeRangeFilter":
            new_filter = TimeRangeFilter(filter_id, column_name, data_set_identifier, 
                                         kwargs.get('null_option', 'ALL_VALUES'),
                                         kwargs.get('min_value_parameter',{'StaticValue': datetime.datetime(2001, 1, 1, 0, 0)}),
                                         kwargs.get('max_value_parameter',{'StaticValue': datetime.datetime(2030, 1, 1, 0, 0)}),
                                         kwargs.get('time_granularity', 'DAY')
                                         )
        else:
            raise ValueError(f"Unsupported filter type: {filter_type}")
        
        self.filters[filter_id] = new_filter
        return self

    def create_filter_control(self, filter_control_id: str, source_filter_id: str, title: str, control_type: str, **kwargs):
        if control_type == "DateTimePicker":
            new_control = FilterDateTimePickerControl(filter_control_id, source_filter_id, title)
            new_control.set_date_time_format(kwargs.get('date_time_format', ''))
            new_control.type = kwargs.get('type', '')
        elif control_type == "Dropdown":
            new_control = FilterListControl(filter_control_id, source_filter_id, title)
            new_control.set_type("MULTI_SELECT")
            new_control.set_select_all_options_visibility("VISIBLE")
        else:
            raise ValueError(f"Unsupported filter control type: {control_type}")
        
        self.filter_controls[filter_control_id] = new_control
        return self

    def add_filter_control_to_sheet(self, sheet_id: str, filter_control_id: str):
        if sheet_id not in self.sheets:
            raise ValueError(f"Sheet {sheet_id} does not exist")
        if filter_control_id not in self.filter_controls:
            raise ValueError(f"Filter control {filter_control_id} does not exist")
        
        self.sheets[sheet_id].add_filter_control(self.filter_controls[filter_control_id])
        return self

    def set_sheet_control_layout(self, sheet_id: str, layout_type: str = "GridLayout"):
        if sheet_id not in self.sheets:
            raise ValueError(f"Sheet {sheet_id} does not exist")
        
        self.sheets[sheet_id].sheet_control_layouts = [{
            "Configuration": {
                layout_type: {
                    "Elements": []
                }
            }
        }]
        return self

    def add_filter_control_to_layout(self, sheet_id: str, filter_control_id: str, column_span: int, row_span: int):
        if sheet_id not in self.sheets:
            raise ValueError(f"Sheet {sheet_id} does not exist")
        if filter_control_id not in self.filter_controls:
            raise ValueError(f"Filter control {filter_control_id} does not exist")
        
        layout_element = {
            "ElementId": filter_control_id,
            "ElementType": "FILTER_CONTROL",
            "ColumnSpan": column_span,
            "RowSpan": row_span
        }
        self.sheets[sheet_id].sheet_control_layouts[0]["Configuration"]["GridLayout"]["Elements"].append(layout_element)
        return self
    
    def create_filter_group(self, group_id: str, dataset_identifier: str):
        if group_id not in self.filter_groups:
            self.filter_groups[group_id] = {
                "dataset_identifier": dataset_identifier,
                "filters": []
            }
        elif self.filter_groups[group_id]["dataset_identifier"] != dataset_identifier:
            raise ValueError(f"Filter group '{group_id}' already exists with a different dataset identifier.")

    def add_filter_group(self, cross_dataset: bool, filter_group_id: str):
        if not self.definition:
            raise ValueError("Definition must be created first")
        
        filter_group = FilterGroup("ALL_DATASETS" if cross_dataset else "ALL_DATASETS", filter_group_id)
        filter_group.set_status("ENABLED")
        
        # Add a default scope configuration
        filter_group.add_scope_configuration("SELECTED_VISUALS", list(self.sheets.keys())[0], list(self.visuals.keys()))
        
        #self.definition.add_filter_group(filter_group)
        return self

    def add_filter_to_group(self, group_id: str, filter_ids: List[str]):
        if group_id not in self.filter_groups:
            raise ValueError(f"Filter group {group_id} does not exist")
        
        group_dataset = self.filter_groups[group_id]["dataset_identifier"]
        
        for filter_id in filter_ids:
            if filter_id not in self.filters:
                raise ValueError(f"Filter {filter_id} does not exist")
            
            filter_object = self.filters[filter_id]
            if filter_object.data_set_identifier != group_dataset:
                raise ValueError(f"Filter {filter_id} (dataset: {filter_object.data_set_identifier}) does not match the dataset of group {group_id} (dataset: {group_dataset})")
            
            filter_config = filter_object.compile()
            if filter_config not in self.filter_groups[group_id]["filters"]:
                self.filter_groups[group_id]["filters"].append(filter_config)

        
    def add_filter_groups_to_definition(self):
        if not self.definition:
            raise ValueError("Definition must be created first")

        # Create a set of existing filter group IDs
        existing_group_ids = {group['FilterGroupId'] for group in self.definition.filter_groups}

        for group_id, group_data in self.filter_groups.items():
            if group_id not in existing_group_ids:
                filter_group = FilterGroup("ALL_DATASETS", group_id)
                filter_group.set_status("ENABLED")
                filter_group.add_scope_configuration("SELECTED_VISUALS", list(self.sheets.keys())[0], list(self.visuals.keys()))
                
                for filter_config in group_data["filters"]:
                    filter_group.filters.append(filter_config)
                
                self.definition.add_filter_group(filter_group)
            else:
                print(f"Warning: Filter group '{group_id}' already exists in the definition. Skipping addition.")
    
    def create_or_operate_line_bar_visual(self, sheet_id: str, visual_type: str, visual_id: str, title: str,
                      x_field: str, x_field_type: str, x_dataset_identifier: str,
                      y_field: str, y_field_type: str, y_dataset_identifier: str,
                      color_field: Optional[str] = None, color_field_type: Optional[str] = None, 
                      color_dataset_identifier: Optional[str] = None,
                      x_date_granularity: Optional[str] = None, 
                      y_aggregation_function: Optional[str] = None,
                      color_date_granularity: Optional[str] = None):
        if sheet_id not in self.sheets:
            raise ValueError(f"Sheet {sheet_id} does not exist")

        visual_classes = {
            "BAR": BarChartVisual,
            "LINE": LineChartVisual,
            "PIE": PieChartVisual,
        }

        if visual_type not in visual_classes:
            raise ValueError(f"Unsupported visual type: {visual_type}")

        visual = visual_classes[visual_type](visual_id)
        #visual.add_title("VISIBLE", "PlainText", title)  # Changed from set_title to add_title

        self._add_axis(visual, x_field, x_field_type, x_dataset_identifier, "x", x_date_granularity)
        self._add_axis(visual, y_field, y_field_type, y_dataset_identifier, "y", y_aggregation_function)
        if color_field:
            self._add_axis(visual, color_field, color_field_type, color_dataset_identifier, "color", color_date_granularity)

        self.visuals[visual_id] = visual
    
        return self
    
    def create_or_operate_table_visual(self, sheet_id: str,  visual_id: str, 
                      x_fields: List[str], x_field_types: List[str], x_dataset_identifier: str,
                      y_fields: List[str], y_field_types: List[str], y_dataset_identifier: str,
                      x_date_granularity: Optional[str] = None, 
                      y_aggregation_function: Optional[str] = None,
                      ):
        if sheet_id not in self.sheets:
            raise ValueError(f"Sheet {sheet_id} does not exist")
        if visual_id not in self.visuals:
            visual = TableVisual(visual_id)
        else:
            visual = self.visuals[visual_id]
        
        #visual.add_title("VISIBLE", "PlainText", title)  # Changed from set_title to add_title
        for x_field, x_field_type in zip(x_fields, x_field_types):
            self._add_axis(visual, x_field, x_field_type, x_dataset_identifier, "x", x_date_granularity)
    
        for y_field, y_field_type in zip(y_fields, y_field_types):
            self._add_axis(visual, y_field, y_field_type, y_dataset_identifier, "y", y_aggregation_function)
       
        

        self.visuals[visual_id] = visual
    
        return self
    

    def _add_axis(self, visual, field, field_type, dataset_identifier, axis_type, additional_param=None):
        field_type = field_type.upper()

        if axis_type == "x":
            if field_type not in ["DIMENSION", "DATE", "MEASURE"]:
                raise ValueError(f"Invalid x-axis type. Must be 'DIMENSION', 'DATE', or 'MEASURE'. Got {field_type}")
            if field_type == "DIMENSION":
                visual.add_categorical_dimension_field(field, dataset_identifier)
            elif field_type == "DATE":
                visual.add_date_dimension_field(field, dataset_identifier, date_granularity=additional_param)
            elif field_type == "MEASURE":
                visual.add_numerical_dimension_field(field, dataset_identifier)
        elif axis_type == "y":
            if field_type not in ["MEASURE", "DATE"]:
                raise ValueError(f"Invalid y-axis type. Must be 'MEASURE' or 'DATE'. Got {field_type}")
            if field_type == "MEASURE":
                visual.add_numerical_measure_field(field, dataset_identifier, aggregation_function=additional_param)
            elif field_type == "DATE":
                visual.add_date_measure_field(field, dataset_identifier, aggregation_function=additional_param)
        elif axis_type == "color":
            visual.add_color(field, dataset_identifier, field_type, date_granularity=additional_param)

    def set_visual_title(self, visual_id: str, title: str, visibility: str = "VISIBLE"):
        if visual_id not in self.visuals:
            raise ValueError(f"Visual {visual_id} does not exist")
        
        self.visuals[visual_id].add_title(visibility, "PlainText", title)
        return self

    def add_visual_to_sheet(self, sheet_id: str, visual_id: str):
        if sheet_id not in self.sheets or visual_id not in self.visuals:
            raise ValueError(f"Sheet {sheet_id} or Visual {visual_id} does not exist")
        
        self.sheets[sheet_id].add_visuals([self.visuals[visual_id]])
        return self

    def add_visual_layout_to_sheet(self, sheet_id: str, visual_id: str, x_position: int, y_position: int, width: int, height: int):
        if sheet_id not in self.sheets or visual_id not in self.visuals:
            raise ValueError(f"Sheet {sheet_id} or Visual {visual_id} does not exist")
        
        self.sheets[sheet_id].add_grid_layout_element(self.visuals[visual_id], width, height, x_position, y_position)
        return self

    def add_sheets_to_analysis(self):
        if not self.definition:
            raise ValueError("Definition must be created first")
        
        for sheet in self.sheets.values():
            self.definition.add_sheet(sheet)
        
        # Add definition to analysis
        self.analysis.add_definition(self.definition)
        
        return self

    def build(self):
        if not self.analysis:
            raise ValueError("Analysis must be created first")
        
        return self.analysis.compile()



@tool
def get_all_datasets_from_quicksight(aws_account_id: str) -> List[Dict[str, str]]:
    """
    Query all dataset and their corresponding ARNs in QuickSight.
    This is the first step for any operation related to QuickSight system.
    Note:The dataset in QuickSight is equivalent to the table in SQL. Therefore, you also need to read the specific schema information in the table through the function('get_table_info') .
    Args:
        aws_account_id (str): The AWS account ID. default is ''

    Returns:
        List[Dict[str, str]]: A list of dictionaries, each containing the name and ARN of a dataset.
    """
    response = client_qs.list_data_sets(AwsAccountId='')
    return [{"name": dataset['Name'], "arn": dataset['Arn']} for dataset in response['DataSetSummaries']]

from botocore.exceptions import ClientError
@tool
def get_analysis_info(analysis_id: str) -> Dict[str, Any]:
    """
    Retrieve information about sheets and filter groups in a QuickSight analysis.

    Parameters:
    analysis_id (str): The ID of the QuickSight analysis to query.

    Returns:
    Dict[str, Any]: A dictionary containing 'Sheets' and 'FilterGroups' information,
                    or an error message if the query fails.

    Example:
    >>> info = get_analysis_info("your-analysis-id")
    >>> print(info)
    """
    try:
        response = client_qs.describe_analysis_definition(
            AwsAccountId='',
            AnalysisId=analysis_id
        )

        return {
            'Sheets': response.get('Sheets', []),
            'FilterGroups': response.get('FilterGroups', [])
        }

    except ClientError as e:
        return {"Error": f"Error retrieving analysis information: {e.response['Error']['Message']}"}
    except Exception as e:
        return {"Error": f"An unexpected error occurred: {str(e)}"}
