import random
import numpy as np
import mesa
import mesa.visualization.modules as viz_modules
import mesa.visualization.UserParam as UserParam

class Miner(mesa.Agent):
    """
    Represents a Bitcoin miner or mining pool in the simulation.
    """
    def __init__(self, unique_id, model, pos, initial_hash_rate, initial_balance=0):
        super().__init__(unique_id, model)
        self.pos = pos
        self.hash_rate = initial_hash_rate
        self.reward_balance = initial_balance
        self.active = True
    
    def mine(self):
        """
        Attempt to mine a block based on the miner's hash rate.
        """
        total_network_hash_rate = self.model.get_total_hash_rate()
        block_found_probability = self.hash_rate / total_network_hash_rate
        
        if random.random() < block_found_probability:
            block_reward = self.model.block_reward
            self.reward_balance += block_reward
            return True
        return False
    
    def adjust_hash_rate(self):
        """
        Dynamically adjust hash rate based on rewards and market conditions.
        """
        reward_threshold = self.model.block_reward * 0.5
        if self.reward_balance < reward_threshold:
            self.hash_rate *= 0.9
            if self.hash_rate < self.model.min_viable_hash_rate:
                self.active = False
    
    def step(self):
        """
        Miner's step function in each simulation iteration.
        """
        if not self.active:
            return
        
        if self.mine():
            self.model.adjust_difficulty()
        
        self.adjust_hash_rate()

class BitcoinMiningModel(mesa.Model):
    """
    Mesa model for simulating Bitcoin mining dynamics.
    """
    def __init__(self, 
                 num_miners=10, 
                 initial_block_reward=6.25, 
                 initial_difficulty=1,
                 min_hash_rate=0.01,
                 max_hash_rate=100,
                 width=10,
                 height=10):
        # Create grid
        self.grid = mesa.space.MultiGrid(width, height, True)
        
        self.schedule = mesa.time.RandomActivation(self)
        self.running = True
        
        # Model parameters
        self.block_reward = initial_block_reward
        self.difficulty = initial_difficulty
        self.min_viable_hash_rate = min_hash_rate
        self.width = width
        self.height = height
        
        # Create miners with varying hash rates
        self.miners = []
        for i in range(num_miners):
            # Randomly place miners on the grid
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            pos = (x, y)
            
            initial_hash_rate = random.uniform(min_hash_rate, max_hash_rate)
            miner = Miner(i, self, pos, initial_hash_rate)
            
            # Place miner on the grid
            self.grid.place_agent(miner, pos)
            
            self.schedule.add(miner)
            self.miners.append(miner)
        
        # Tracking metrics
        self.blocks_mined = 0
        self.total_simulation_time = 0
        self.block_times = []
        
        # Datacollector for visualization
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Total_Hash_Rate": lambda m: m.get_total_hash_rate(),
                "Difficulty": lambda m: m.difficulty,
                "Blocks_Mined": lambda m: m.blocks_mined
            },
            agent_reporters={
                "Hash_Rate": lambda a: a.hash_rate,
                "Reward_Balance": lambda a: a.reward_balance,
                "Active": lambda a: 1 if a.active else 0
            }
        )
    
    def get_total_hash_rate(self):
        """
        Calculate total network hash rate.
        """
        return sum(agent.hash_rate for agent in self.schedule.agents if agent.active)
    
    def adjust_difficulty(self):
        """
        Adjust mining difficulty based on block mining rate.
        """
        self.blocks_mined += 1
        
        if self.blocks_mined % 2016 == 0:
            avg_block_time = np.mean(self.block_times[-2016:]) if self.block_times else 10
            target_block_time = 10
            
            if avg_block_time < target_block_time:
                self.difficulty *= 1.1
            else:
                self.difficulty *= 0.9
    
    def step(self):
        """
        Model step function.
        """
        self.schedule.step()
        self.datacollector.collect(self)
        self.total_simulation_time += 1
    
    def run_simulation(self, max_steps=1000):
        """
        Run the entire simulation.
        """
        while self.running and self.total_simulation_time < max_steps:
            self.step()

# Visualization elements
def miner_portrayal(agent):
    """
    Create visual representation of miners for the grid.
    """
    if not agent:
        return
    
    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "r": 0.5,
        "Layer": 0,
        "Color": "green" if agent.active else "red",
        "text": f"HR: {agent.hash_rate:.2f}\nReward: {agent.reward_balance:.2f}"
    }
    return portrayal

# Visualization setup
def run_simulation_server():
    # Chart modules for visualization
    hash_rate_chart = viz_modules.ChartModule([
        {"Label": "Total_Hash_Rate", "Color": "Blue"},
        {"Label": "Difficulty", "Color": "Red"}
    ])
    
    blocks_mined_chart = viz_modules.ChartModule([
        {"Label": "Blocks_Mined", "Color": "Green"}
    ])
    
    # Grid visualization of miners
    grid = viz_modules.CanvasGrid(miner_portrayal, 10, 10, 500, 500)
    
    # Server setup with custom parameters
    server = mesa.visualization.ModularServer(
        BitcoinMiningModel, 
        [grid, hash_rate_chart, blocks_mined_chart],
        "Bitcoin Mining Simulation",
        {
            "num_miners": UserParam.Slider("Number of Miners", 10, 1, 50),
            "initial_block_reward": UserParam.Slider("Initial Block Reward", 6, 1, 10, 1),
            "initial_difficulty": UserParam.Slider("Initial Difficulty", 1, 0.1, 10, 0.1),
            "min_hash_rate": UserParam.Slider("Minimum Hash Rate", 1, 0.1, 10, 0.1),
            "max_hash_rate": UserParam.Slider("Maximum Hash Rate", 100, 10, 500, 10),
            "width": UserParam.Slider("Grid Width", 10, 5, 20, 1),
            "height": UserParam.Slider("Grid Height", 10, 5, 20, 1)
        }
    )
    
    return server

# Main entry point
if __name__ == "__main__":
    # Run the visualization server
    server = run_simulation_server()
    server.port = 8521  # default Mesa port
    server.launch()
