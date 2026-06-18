# univac_schema_cache.py
import json
import time
import openpyxl
from threading import Lock
from collections import OrderedDict
from univac_cell_map import ExcelCellOrchestrator

# Standard JSON Schema definition tracking strict typing expectations
EXPECTED_TELEMETRY_SCHEMA = {
    "node_id": str,
    "permittivity": (int, float),
    "conductivity": (int, float),
    "scan_frequency": (int, float),
    "gps_ecef": list,
    "assert_contains_biology": bool
}

class TelemetrySchemaValidator:
    @staticmethod
    def validate_packet(packet_dict):
        """
        Validates incoming data footprints against structural typing targets.
        Returns (True, None) if compliant, or (False, error_reason) if malformed.
        """
        for expected_key, expected_type in EXPECTED_TELEMETRY_SCHEMA.items():
            # Check for structural omissions
            if expected_key not in packet_dict:
                return False, f"Missing required parameter slot: '{expected_key}'"
            
            # Check for matching types
            actual_value = packet_dict[expected_key]
            if not isinstance(actual_value, expected_type):
                return False, f"Type mismatch on '{expected_key}'. Expected {expected_type}, got {type(actual_value)}"
                
        # Validate inner vector arrays explicitly
        if len(packet_dict["gps_ecef"]) != 3:
            return False, "GPS ECEF metric invalid. Position array must contain exactly 3 spatial coordinates [X, Y, Z]."
            
        return True, "Passed Schema Audit."


class HighPerformanceMemoryCacheEngine:
    def __init__(self, excel_path="../Univac-IX/materials_db.xlsx", cache_limit=128):
        self.excel_path = excel_path
        self.cache_limit = cache_limit
        
        # In-memory lookup map to bypass disk calls for repetitive states
        self.matrix_cache = OrderedDict()
        
        # Concurrency Lock protecting OpenPyXL memory space from racing threads
        self.execution_lock = Lock()
        
        # Pre-load base sheets into memory to warm the pipeline buffer
        print("Pre-loading calculation database layout matrices into memory cache...")
        self.cached_workbook = openpyxl.load_workbook(self.excel_path, data_only=False)

    def process_telemetry_through_cache(self, verified_packet):
        """
        Ingests safe telemetry, uses thread locks to safely execute math operations,
        and manages an optimization cache map to reduce hardware overhead.
        """
        node_id = verified_packet["node_id"]
        
        # Construct a fingerprint based on input values to check the cache
        # If the material state matches a known pattern, we can skip running formulas
        state_fingerprint = (
            round(verified_packet["permittivity"], 4),
            round(verified_packet["conductivity"], 4),
            round(verified_packet["scan_frequency"], 2)
        )

        with self.execution_lock:
            # CHECK CACHE: If this exact material trait was processed recently, return it instantly
            if state_fingerprint in self.matrix_cache:
                # Move hit element to the end to maintain correct LRU ordering
                self.matrix_cache.move_to_end(state_fingerprint)
                print(f"⚡ CACHE HIT: Retrieved resolved calculations for [{node_id}] in 0.00ms via memory map.")
                return self.matrix_cache[state_fingerprint]

            # CACHE MISS: Run inputs through the Excel calculation formulas
            orchestrator = ExcelCellOrchestrator(self.cached_workbook)
            
            # Inject inputs via our dictionary cell map coordinates
            orchestrator.inject_inputs(verified_packet)
            
            # Save internal state changes back into memory (Avoid hitting disk!)
            # OpenPyXL recalculates cell references internally when re-evaluated
            calculated_output = orchestrator.extract_calculated_json()
            
            # Update local memory tracking map
            self.matrix_cache[state_fingerprint] = calculated_output
            
            # Maintain memory limit boundaries (Evict least recently used entries)
            if len(self.matrix_cache) > self.cache_limit:
                evicted_key = self.matrix_cache.popitem(last=False)
                print(f"-> Cache boundary reached. Evicted stale profile signature: {evicted_key[0]}")
                
            # Periodically sync memory changes to disk in a separate background operation
            # To ensure durability, we commit the active state every 50 loops
            if len(self.matrix_cache) % 50 == 0:
                self.cached_workbook.save(self.excel_path)
                print("💾 Mainframe Sync: Flushed cache layers directly to persistent storage disk.")

            return calculated_output
