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
        self.entry_time = 0  # Default to 0, will be set during model initialization
    
    def mine(self):
        """
        Attempt to mine a block based on the miner's hash rate and simulated Bitcoin price.
        """
        total_network_hash_rate = self.model.get_total_hash_rate()
        block_found_probability = self.hash_rate / total_network_hash_rate
        
        if random.random() < block_found_probability:
            # Dynamically adjust block reward based on simulated Bitcoin price
            block_reward = self.model.block_reward * self.model.bitcoin_price
            self.reward_balance += block_reward
            return True
        return False
    
    def adjust_hash_rate(self):
        """
        Dynamically adjust hash rate based on Bitcoin price and rewards.
        """
        # More aggressive hash rate adjustment based on price and rewards
        price_factor = self.model.bitcoin_price
        reward_factor = self.reward_balance / (self.model.block_reward * price_factor)
        
        # Adjust hash rate based on profitability
        if reward_factor < 0.5:
            # Reduce hash rate if not profitable
            self.hash_rate *= max(0.7, 1 - (1 - reward_factor))
        else:
            # Increase hash rate if profitable
            self.hash_rate *= min(1.3, 1 + (reward_factor - 0.5))
        
        # Ensure hash rate stays within reasonable bounds
        self.hash_rate = max(0.01, min(self.hash_rate, 100))
        
        # Deactivate if hash rate becomes too low
        if self.hash_rate < 0.1:
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
                 initial_block_reward=6.25):
        # Tracking metrics
        self.total_simulation_time = 0
        self.blocks_mined = 0
        
        # Create grid
        self.width = 10
        self.height = 10
        self.grid = mesa.space.MultiGrid(self.width, self.height, True)
        
        self.schedule = mesa.time.RandomActivation(self)
        self.running = True
        
        # Model parameters
        self.block_reward = initial_block_reward
        self.difficulty = 1
        self.bitcoin_price = 1  # Start with a baseline price
        
        # Price volatility simulation
        self.price_history = [1]
        self.difficulty_history = [1]
        
        # Create initial miners with varying hash rates
        self.miners = []
        self.next_miner_id = 0
        self.create_initial_miners(num_miners)
        
        # Datacollector for visualization
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Total_Hash_Rate": lambda m: m.get_total_hash_rate(),
                "Difficulty": lambda m: m.difficulty,
                "Blocks_Mined": lambda m: m.blocks_mined,
                "Bitcoin_Price": lambda m: m.bitcoin_price,
                "Active_Miners": lambda m: len([a for a in m.schedule.agents if a.active])
            },
            agent_reporters={
                "Hash_Rate": lambda a: a.hash_rate,
                "Reward_Balance": lambda a: a.reward_balance,
                "Active": lambda a: 1 if a.active else 0
            }
        )
    
    def create_initial_miners(self, num_miners):
        """
        Create initial set of miners with unique IDs.
        """
        for _ in range(num_miners):
            self.add_new_miner()
    
    def add_new_miner(self):
        """
        Add a new miner to the simulation based on market conditions.
        """
        # Randomly place miners on the grid
        x = self.random.randrange(self.width)
        y = self.random.randrange(self.height)
        pos = (x, y)
        
        # Determine initial hash rate based on market conditions
        # More attractive market conditions lead to higher initial hash rates
        market_attractiveness = self.bitcoin_price * self.block_reward
        initial_hash_rate = random.uniform(0.1, min(10, market_attractiveness))
        
        miner = Miner(self.next_miner_id, self, pos, initial_hash_rate)
        # Set entry time for the new miner
        miner.entry_time = self.total_simulation_time
        
        # Place miner on the grid
        self.grid.place_agent(miner, pos)
        
        self.schedule.add(miner)
        self.miners.append(miner)
        self.next_miner_id += 1
    
    
    def simulate_bitcoin_price(self):
        """
        Simulate Bitcoin price with increased volatility and random shocks.
        """
        last_price = self.price_history[-1]
        
        # Random walk with higher volatility and occasional shocks
        base_volatility = 0.25  # Increased standard deviation for regular fluctuations
        random_walk = random.gauss(0, base_volatility)
        
        # Add more frequent large shocks
        if random.random() < 0.2:  # 20% chance of a significant price change
            shock_magnitude = random.choice([-0.7, -0.5, -0.3, 0.3, 0.5, 0.7])
            random_walk += shock_magnitude
        
        # Calculate the new price and ensure it remains within realistic bounds
        new_price = last_price * (1 + random_walk)
        new_price = max(0.1, min(new_price, 50))  # Prevent the price from crashing or skyrocketing
        
        self.bitcoin_price = new_price
        self.price_history.append(new_price)

    
    def get_total_hash_rate(self):
        """
        Calculate total network hash rate.
        """
        return sum(agent.hash_rate for agent in self.schedule.agents if agent.active)
    

    def adjust_difficulty(self):
        """
        Adjust difficulty based on block mining time and network hash rate.
        """
        self.blocks_mined += 1
        
        # Track the time taken to mine blocks
        if self.blocks_mined == 1:
            self.last_difficulty_adjustment_time = self.total_simulation_time
        
        if self.blocks_mined % 50 == 0:
            # Calculate time elapsed since last adjustment
            time_elapsed = self.total_simulation_time - self.last_difficulty_adjustment_time
            self.last_difficulty_adjustment_time = self.total_simulation_time
            
            # Target time for mining 50 blocks (e.g., 500 steps)
            target_time = 500
            
            # Adjust difficulty based on elapsed time
            if time_elapsed < target_time:
                # Blocks are mined too quickly, increase difficulty
                self.difficulty *= 1.1
            elif time_elapsed > target_time:
                # Blocks are mined too slowly, decrease difficulty
                self.difficulty *= 0.9
            
            # Store difficulty history for visualization
            self.difficulty_history.append(self.difficulty)
            
            # Probabilistically add new miners based on market conditions
            market_attractiveness = self.bitcoin_price * self.block_reward
            if random.random() < market_attractiveness / 10:
                self.add_new_miner()

    
    def step(self):
        """
        Model step function.
        """
        # Simulate Bitcoin price volatility
        self.simulate_bitcoin_price()
        
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
        {"Label": "Bitcoin_Price", "Color": "Green"},
        {"Label": "Active_Miners", "Color": "Purple"}
    ])
    
    difficulty_chart = viz_modules.ChartModule([
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
        [grid, hash_rate_chart, difficulty_chart, blocks_mined_chart],
        "Bitcoin Mining Simulation",
        {
            "num_miners": UserParam.Slider("Number of Miners", 10, 1, 50)
        }
    )
    
    return server

# Main entry point
if __name__ == "__main__":
    # Run the visualization server
    server = run_simulation_server()
    server.port = 8521  # default Mesa port
    server.launch()
