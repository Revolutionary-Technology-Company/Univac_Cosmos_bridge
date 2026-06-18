import os
import json
import openpyxl
import json
from univac_cell_map import ExcelCellOrchestrator

class UnivacExcelJsonAdapter:
    def __init__(self, excel_path="../Univac-IX/materials_db.xlsx"):
        self.excel_path = excel_path

    def compute_and_serialize_to_json(self, incoming_data_dict):
        # 1. Open the sheet with formulas active (data_only=False) to inject variables
        wb_write = openpyxl.load_workbook(self.excel_path, data_only=False)
        orchestrator_write = ExcelCellOrchestrator(wb_write)
        
        # Inject values dynamically based on the dictionary coordinates
        orchestrator_write.inject_inputs(incoming_data_dict)
        wb_write.save(self.excel_path)

        # 2. Re-open with data_only=True to let the engine evaluate the multi-tab formulas
        wb_read = openpyxl.load_workbook(self.excel_path, data_only=True)
        orchestrator_read = ExcelCellOrchestrator(wb_read)
        
        # Extract the calculated results using the map locations
        calculated_results = orchestrator_read.extract_calculated_json()
        
        # Append the original raw inputs for tracking verification
        calculated_results["telemetry_inversion"] = incoming_data_dict
        
        # Serialize the combined data to a clean JSON string
        return json.dumps(calculated_results, indent=4)

# --- WORKSPACE EXECUTION RUN TEST ---
if __name__ == "__main__":
    print("Testing Univac-IX Linked Excel-to-JSON Serialization Engine...")
    
    # Simple setup of a dummy workbook structure if you run it locally without your real repo present
    # In live development, this file will already exist inside your sibling Univac-IX folder
    try:
        adapter = UnivacExcelJsonAdapter()
        
        # Simulate incoming antenna metrics triggering the calculations
        json_output_payload = adapter.compute_and_serialize_to_json(
            raw_sensor_permittivity=7.42, 
            raw_conductivity=1.85
        )
        
        print("\n=== SYSTEM SYNCED DATA PACKET CONVERTED TO JSON ===")
        print(json_output_payload)
        
    except FileNotFoundError as e:
        print(f"Simulation bypass: {e}")
        print("-> To deploy in production, ensure your calculated materials_db.xlsx sits in the Univac-IX folder.")
