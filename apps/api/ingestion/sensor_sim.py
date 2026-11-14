"""
PENELOPE Backend - Simulated Sensor Generator (Hard Rule 3 Compliance)
"""

from app.sim.sensors import run_sensor_simulation

class SensorSimulatorDaemon:
    def __init__(self):
        pass

    def generate_simulated_readings(self, db):
        count = run_sensor_simulation(num_steps=1)
        return [{"count": count, "source": "simulated"}]

if __name__ == "__main__":
    run_sensor_simulation(num_steps=1)
