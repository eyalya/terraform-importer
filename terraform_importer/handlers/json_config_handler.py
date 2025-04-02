class JsonConfigHandler:
    @staticmethod
    def replace_variables(json_data: dict, variables: dict) -> dict:
        """
        Replaces all 'var.' references in the JSON data with their corresponding values
        from the variables dictionary.
        
        Args:
            json_data (dict): The JSON data containing potential 'var.' references
            variables (dict): Dictionary containing variable names and their values
            
        Returns:
            dict: JSON data with variables replaced by their values
        """
        def replace_in_value(value):
            if isinstance(value, str) and value.startswith("var."):
                var_name = value.replace("var.", "", 1)
                return variables.get(var_name, value)
            elif isinstance(value, dict):
                return {k: replace_in_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [replace_in_value(item) for item in value]
            return value
        
        return replace_in_value(json_data)

    @staticmethod
    def simplify_references(json_data: dict) -> dict:
        """
        Cleans the JSON data by removing all '${var...}' references.
        
        Args:
            json_data (dict): The JSON data to clean
        """
        if isinstance(json_data, dict):
            new_dict = {}
            for key, value in json_data.items():
                if isinstance(value, dict) and "references" in value:
                    # If it's a reference block with a single value, simplify it
                    if isinstance(value["references"], list) and len(value["references"]) == 1:
                        if "value" in value["references"][0]:
                            new_dict[key] = value["references"][0]["value"]
                            continue
                # Recursively process nested structures
                new_dict[key] = JsonConfigHandler.simplify_references(value)
            return new_dict
        elif isinstance(json_data, list):
            #return [JsonConfigHandler.simplify_references(item) for item in json_data]
            #### modified the function to handle/simplify references in lists
            # Process each item in the list recursively and simplify references if present
            new_list = []
            for item in json_data:
                if isinstance(item, dict) and "references" in item:
                    # If the item is a dict with references, simplify it
                    if isinstance(item["references"], list) and len(item["references"]) == 1:
                        if "value" in item["references"][0]:
                            new_list.append(item["references"][0]["value"])
                        else:
                            new_list.append(item)
                    else:
                        new_list.append(item)
                else:
                    # Recursively process nested items
                    new_list.append(JsonConfigHandler.simplify_references(item))
            return new_list

        return json_data
        
    @staticmethod
    def simplify_constant_values(json_data: dict) -> dict:
        """
        Simplifies the JSON data by converting constant_value structures to direct values.
        
        Args:
            json_data (dict): The JSON data to simplify
            
        Returns:
            dict: Simplified JSON data
        """
        if isinstance(json_data, dict):
            new_dict = {}
            for key, value in json_data.items():
                if isinstance(value, dict) and "constant_value" in value:
                    # If it's a constant_value block, replace with the direct value
                    new_dict[key] = value["constant_value"]
                else:
                    # Recursively process nested structures
                    new_dict[key] = JsonConfigHandler.simplify_constant_values(value)
            return new_dict
        elif isinstance(json_data, list):
            #return [JsonConfigHandler.simplify_constant_values(item) for item in json_data]
            # modify the function to handle lists that contain dictionaries with constant_value fields
            new_list = []
            for item in json_data:
                if isinstance(item, dict) and "constant_value" in item:
                    new_list.append(item["constant_value"])
                else:
                    new_list.append(JsonConfigHandler.simplify_constant_values(item))
            return new_list
        return json_data
    
    @staticmethod
    def extract_provider_config_keys(json_data: dict) -> dict:
        """
        Recursively scans JSON data and extracts all provider_config_key values with their full paths.
        
        Args:
            json_data (dict): The JSON data to scan
            
        Returns:
            dict: Dictionary with full paths as keys and provider_config_key values as values
        """
        result = {}
        
        def scan_json(data, path):
            if isinstance(data, dict):
                for key, value in data.items():
                    # Handle special path cases
                    if key == "module_calls":
                        new_path = f"{path}.module" if path else "module"
                    elif key == "resources":
                        new_path = path  # Remove 'resources' from path
                    else:
                        new_path = f"{path}.{key}" if path else key
                    
                    if key == "provider_config_key" and isinstance(value, str):
                        result[path] = value
                    
                    scan_json(value, new_path)
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    # Use the item's address if available, otherwise fall back to index
                    if isinstance(item, dict) and "address" in item:
                        if path == "":
                            new_path = item['address']
                        else:
                            new_path = f"{path}.{item['address']}"
                    else:
                        new_path = f"{path}[{i}]"
                    scan_json(item, new_path)
        
        scan_json(json_data, "")
        return result

    @staticmethod
    def edit_provider_config(json_data: dict) -> dict:
        stript_config = JsonConfigHandler.replace_variables(json_data["configuration"]["provider_config"], json_data["variables"])
        stript_config = JsonConfigHandler.simplify_references(stript_config)
        stript_config = JsonConfigHandler.simplify_constant_values(stript_config)
        
        return stript_config
    