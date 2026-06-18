import numpy as np

class MainframeRadiationSafetyGuard:
    def __init__(self):
        # Maximum allowable frequency for penetrative imaging (300 GHz - upper Terahertz band)
        # Anything higher borders on ionizing radiation or unsafe spectrum paths
        self.IONIZATION_CUTOFF_HZ = 300e9 
        
        # Public safety power density threshold (10 Watts per meter squared, FCC/ICNIRP standard)
        self.MAX_SAFE_POWER_DENSITY = 10.0 

    def evaluate_scan_safety(self, center_frequency_hz, output_power_watts, antenna_gain, proximity_distance_meters, contains_biology):
        """
        Intercepts pending antenna transmission arrays and dynamically 
        calculates safety compliance before hardware validation.
        """
        # 1. PRIMARY PROTECTION: Ionization spectrum check
        if center_frequency_hz >= self.IONIZATION_CUTOFF_HZ:
            return {
                "status": "BLOCKED_CRITICAL",
                "reason": "Forbidden Frequency. Operation crosses the ionizing radiation boundary.",
                "allowed_power_scaling": 0.0
            }
            
        # If no biological tissue is detected in the line of sight, allow operational latitude
        if not contains_biology:
            return {"status": "PASSED_UNRESTRICTED", "reason": "No biological markers present in scan sector.", "allowed_power_scaling": 1.0}
            
        # 2. THERMAL PROTECTION: Calculate power flux density if humans/animals/plants are near
        # Protect against division-by-zero if object is directly on the antenna element
        clamped_distance = max(proximity_distance_meters, 0.1)
        power_density = (output_power_watts * antenna_gain) / (4.0 * np.pi * (clamped_distance ** 2))
        
        # 3. CLOSED-LOOP CORRECTION: If unsafe, calculate the exact mitigation scale factor
        if power_density > self.MAX_SAFE_POWER_DENSITY:
            # Scale power back down to meet safety thresholds exactly
            mitigation_factor = self.MAX_SAFE_POWER_DENSITY / power_density
            return {
                "status": "AUTOCORRECTED_REDUCED_POWER",
                "reason": f"Power density ({power_density:.2f} W/m²) exceeds safety ceilings near biological tissue.",
                "allowed_power_scaling": mitigation_factor
            }
            
        return {
            "status": "PASSED_SAFE",
            "reason": f"Radiation density compliant at {power_density:.4f} W/m².",
            "allowed_power_scaling": 1.0
        }

# --- ACTIVE PIPELINE FIRETRIAL TEST ---
if __name__ == "__main__":
    print("Engaging Sovereign Radiation Safety Guard Modules...")
    guard = MainframeRadiationSafetyGuard()
    
    # Test Scenario A: An anomalous or corrupted camera sensor requests a high-frequency UV/X-Ray sweep
    print("\n[Scanning Telemetry Request A...]")
    alert_alpha = guard.evaluate_scan_safety(
        center_frequency_hz=500e12, # Extreme ionizing optical band
        output_power_watts=0.5, antenna_gain=1.2, proximity_distance_meters=2.0, contains_biology=True
    )
    print(f"Mainframe Decision: {alert_alpha['status']} -> {alert_alpha['reason']}")
    
    # Test Scenario B: A vehicle radar array attempts a high-power scan near a pedestrian
    print("\n[Scanning Telemetry Request B...]")
    alert_beta = guard.evaluate_scan_safety(
        center_frequency_hz=24.2e9,  # Safe radar frequency
        output_power_watts=15.0,    # Unsafely amplified power setting
        antenna_gain=8.0,           # Highly directional high-gain antenna
        proximity_distance_meters=1.5, # Biological target is standing close
        contains_biology=True       # Classified as organic tissue by your Cole-Cole/Univac engine
    )
    print(f"Mainframe Decision: {alert_beta['status']}")
    print(f"Details: {alert_beta['reason']}")
    print(f"Enforced Action Matrix: Hardware output throttled to {alert_beta['allowed_power_scaling']*100:.2f}% power output.")
