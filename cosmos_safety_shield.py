import numpy as np

class CosmosBiologicalShieldEngine:
    def __init__(self):
        # Establish maximum permissible exposure thresholds (W/m^2) for diverse biological states
        self.BIOLOGICAL_THRESHOLDS = {
            "HUMAN": 10.0,       # Strict thermal limits for human tissue
            "SEA_LIFE": 10.0,    # High electrical conductivity water boundary mapping
            "ROOTS": 25.0,       # Protection for root-cap osmotic moisture profiles
            "PLANTS": 50.0,      # Capping threshold to prevent chlorophyll thermal degradation
            "SOIL_MICROBE": 100.0 # Upper limit to protect subterranean fungal and bacterial biomes
        }
        
        # Default safety fallback padding layer (meters) added to the calculated radius
        self.SAFETY_BUFFER_METERS = 0.25

    def calculate_shield_radius(self, bio_type, output_power_watts, antenna_gain):
        """
        Dynamically calculates the 3D safety radius required around a specific 
        organism classification based on current scanning energy telemetry.
        """
        # Resolve target biological profile threshold, fallback to human limits if unknown
        threshold = self.BIOLOGICAL_THRESHOLDS.get(bio_type.upper(), 10.0)
        
        # Standard inverse-square isolation calculation
        raw_radius = np.sqrt((output_power_watts * antenna_gain) / (4.0 * np.pi * threshold))
        
        # Return total radius with defensive buffer padding included
        return raw_radius + self.SAFETY_BUFFER_METERS

    def generate_exclusion_sphere_points(self, center_xyz, radius, num_points=100):
        """
        Generates a 3D coordinate point matrix representing the surface 
        of the safety shield. Ready for direct injection into the Cosmos scene point cloud.
        """
        points = []
        # Procedural parametric sphere generation loop
        for i in range(num_points):
            # Calculate polar and azimuthal angles uniformly distributed
            theta = 2.0 * np.pi * np.random.rand()
            phi = np.arccos(2.0 * np.random.rand() - 1.0)
            
            # Map sphere surface coordinates
            x = center_xyz[0] + radius * np.sin(phi) * np.cos(theta)
            y = center_xyz[1] + radius * np.sin(phi) * np.sin(theta)
            z = center_xyz[2] + radius * np.cos(phi)
            
            points.append([x, y, z])
            
        return np.array(points)

    def generate_openusd_shield_metadata(self, bio_id, bio_type, center_xyz, radius):
        """
        Formats the safety shield parameters as an immutable OpenUSD geometric 
        primitive representation for your NVIDIA Cosmos rendering workspaces.
        """
        # Generates a clear USD text schema snippet representing a physical bounding shield
        usd_snippet = f"""
        def Sphere "SafetyShield_{bio_type}_{bio_id}" (
            prepend apiSchemas = ["GeomModelAPI"]
        ) {{
            double radius = {radius:.4f}
            double3 xformOp:translate = {tuple(center_xyz)}
            uniform token[] xformOpOrder = ["xformOp:translate"]
            color3f primvars:displayColor = [(1.0, 0.0, 0.0)] # Red Warning Boundary
            custom string safety_classification = "{bio_type}"
        }}
        """
        return usd_snippet.strip()

# --- MAIN ENGINE LIFECYCLE RUNTIME TEST ---
if __name__ == "__main__":
    print("Initializing Sovereign NVIDIA Cosmos 3D Biological Safety Shield Engine...")
    shield_engine = CosmosBiologicalShieldEngine()
    
    # Simulation: A smart car scanner is generating high power pulses (50W) near an oak tree and a human
    scanner_power = 50.0  # Watts
    scanner_gain = 4.5    # Antenna directionality index
    
    # Target Profiles discovered by your Univac-IX classification ledger
    targets = [
        {"id": 101, "type": "HUMAN", "loc": np.array([12.5, 4.2, 0.0])},
        {"id": 102, "type": "ROOTS", "loc": np.array([8.0, -1.5, -2.1])},
        {"id": 103, "type": "PLANTS", "loc": np.array([8.0, 3.0, 1.5])}
    ]
    
    print("\n=== GENERATING 3D VIRTUAL EXCLUSION BOUNDARIES ===")
    for target in targets:
        # Step A: Compute custom safety radius per biological envelope rules
        r_shield = shield_engine.calculate_shield_radius(
            bio_type=target["type"], 
            output_power_watts=scanner_power, 
            antenna_gain=scanner_gain
        )
        
        # Step B: Compile OpenUSD rendering commands for Cosmos injection
        usd_definition = shield_engine.generate_openusd_shield_metadata(
            bio_id=target["id"], 
            bio_type=target["type"], 
            center_xyz=target["loc"], 
            radius=r_shield
        )
        
        print(f"\n[Target ID {target['id']} - {target['type']} Locked]")
        print(f"-> Calculated Exclusion Shield Zone Radius: {r_shield:.4f} meters")
        print("-> Generated OpenUSD Script for Cosmos Spatial Scene:")
        print(usd_definition)

import numpy as np

class MainframeRayTracingSafetyEngine:
    @staticmethod
    def test_beam_intersection(ray_origin, ray_direction, shield_center, shield_radius):
        """
        Calculates whether a directional scanner beam path intersects an active 
        biological safety shield sphere using a fast quadratic geometric solver.
        """
        # Ensure the direction vector is a true normalized unit vector
        d = ray_direction / np.linalg.norm(ray_direction)
        o = np.array(ray_origin, dtype=float)
        c = np.array(shield_center, dtype=float)
        r = float(shield_radius)
        
        # Calculate vector pointing from shield center to scanner origin
        oc = o - c
        
        # Compute quadratic coefficients (where A = 1 because d is normalized)
        B = 2.0 * np.dot(d, oc)
        C = np.dot(oc, oc) - (r ** 2)
        
        # Calculate the mathematical discriminant (delta)
        discriminant = (B ** 2) - (4.0 * C)
        
        if discriminant < 0:
            # No real roots exist -> The beam line misses the sphere completely
            return {"hit": False, "entry_distance": None}
            
        # Calculate the intersection entry point distances using quadratic formula
        t1 = (-B - np.sqrt(discriminant)) / 2.0
        t2 = (-B + np.sqrt(discriminant)) / 2.0
        
        # Find the closest intersection path step in front of the scanner (t > 0)
        if t1 > 0:
            return {"hit": True, "entry_distance": t1}
        elif t2 > 0:
            # Scanner origin is inside the safety buffer shield boundary
            return {"hit": True, "entry_distance": 0.0}
            
        # The shield sits behind the direction of the scanner's transmission path
        return {"hit": False, "entry_distance": None}

    def process_global_safety_audit(self, scanner_id, origin, direction, active_shields):
        """
        Audits a pending scanner beam path against all registered biological shields 
        (Humans, Marine Life, Roots, Plants) before allowing active hardware pulse.
        """
        print(f"Auditing safety profile for Scanner Array Node [{scanner_id}]...")
        
        for shield in active_shields:
            result = self.test_beam_intersection(
                ray_origin=origin,
                ray_direction=direction,
                shield_center=shield["center"],
                shield_radius=shield["radius"]
            )
            
            if result["hit"]:
                print(f"⚠️  CRITICAL SAFETY VIOLATION DETECTED!")
                print(f"-> Beam intersects protected [{shield['type']}] space (Shield ID: {shield['id']})")
                print(f"-> Impact point predicted at {result['entry_distance']:.4f} meters along sightline path.")
                return {
                    "action": "FORCE_THROTTLE_POWER",
                    "offending_shield_id": shield["id"],
                    "entry_distance": result["entry_distance"]
                }
                
        print("✅ Safety check passed. Scan vector cleared for transmission.")
        return {"action": "AUTHORIZE_SCAN_FULL_POWER", "offending_shield_id": None, "entry_distance": None}

# --- MAINFRAME ACTIVE RUNTIME VALIDATION ---
if __name__ == "__main__":
    engine = MainframeRayTracingSafetyEngine()
    
    # 1. Define active biological safety shields compiled from your Univac-IX database
    global_shield_matrix = [
        {"id": 401, "type": "HUMAN", "center": np.array([10.0, 0.0, 0.0]), "radius": 2.5},
        {"id": 402, "type": "ROOTS", "center": np.array([3.0, 5.0, -1.0]), "radius": 1.2},
        {"id": 403, "type": "PLANTS", "center": np.array([0.0, -8.0, 2.0]), "radius": 1.8}
    ]
    
    # Test Scenario A: A drone antenna at origin (0,0,0) targets directly down the X-axis (1,0,0)
    # This vector drives right into the Human safety shield situated at coordinates (10,0,0)
    print("\n--- TEST CASE A: TARGETING X-AXIS VECTOR ---")
    drone_origin = [0.0, 0.0, 0.0]
    beam_vector_a = [1.0, 0.0, 0.0] # Firing along the positive X-axis
    
    audit_a = engine.process_global_safety_audit(
        scanner_id="DRONE_RADAR_01", origin=drone_origin, direction=beam_vector_a, active_shields=global_shield_matrix
    )
    
    # Test Scenario B: The same drone re-angles its array to clear the protected assets
    print("\n--- TEST CASE B: TARGETING ADJUSTED CLEAR VECTOR ---")
    beam_vector_b = [1.0, 1.0, 1.0] # Angling up and away from boundaries
    
    audit_b = engine.process_global_safety_audit(
        scanner_id="DRONE_RADAR_01", origin=drone_origin, direction=beam_vector_b, active_shields=global_shield_matrix
    )
