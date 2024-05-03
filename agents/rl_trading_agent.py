from agents.trading_agent import TradingAgent

from tensorforce.agents import Agent as TF_Agent
from tensorforce.environments import Environment


T = 10  # Nombre de pas de temps
N = 5   # Nombre de niveaux de prix

network_spec = [
    {'type': 'conv2d', 'size': 32, 'window': (1, 3), 'stride': 1},
    {'type': 'conv2d', 'size': 32, 'window': (1, 3), 'stride': 1},
    {'type': 'flatten'},
    {'type': 'dense', 'size': 64},
    {'type': 'internal_attention', 'size': 64},
    {'type': 'dueling', 'architecture': 'state-action'}
]

agent_config = {
    'states': {'type': 'float', 'shape': (T, 4, N)},
    'actions': {'type': 'int', 'num_values': 3 * N},
    'network': network_spec,
    'memory': 10000,
    'batch_size': 64,
    'learning_rate': 1e-3,
    'update_frequency': 1
}


class TradingEnvironment(Environment):
    def __init__(self):
        self.data = None
        self.current_step = 0  # indice pour gérer les données
        self.current_state = None
        self.done = False

    def reset(self):
        # Utiliser self.data pour définir l'état initial
        self.current_step = 0
        self.current_state = self.data.iloc[self.current_step]
        self.done = False
        return self.current_state

    def step(self, action):
        # Utiliser self.data pour obtenir l'état suivant
        if self.current_step >= len(self.data) - 1:
            self.done = True
            next_state = None
        else:
            self.current_step += 1
            next_state = self.data.iloc[self.current_step]
        reward = self.compute_reward(action)  # Vous devez définir cette méthode
        self.current_state = next_state
        return next_state, reward, self.done

    def states(self):
        # Définir la structure de l'état observé par les agents
        return {'type': 'float', 'shape': (10, 4, 5)}

    def actions(self):
        # Définir les actions possibles dans l'environnement
        return {'type': 'int', 'num_values': 15}  # Exemple: 5 niveaux, 3 actions par niveau


class RL_Agent(TradingAgent):
    def __init__(self, id, config):
        super().__init__(id)
        self.environment = TradingEnvironment()
        self.config = config
        self.agent = TF_Agent.create(
            agent='dueling_dqn',
            environment=dict(states=agent_config['states'], actions=agent_config['actions']),
            network=config['network'],
            memory=config['memory'],
            update=dict(unit='timesteps', batch_size=config['batch_size']),
            optimizer=dict(type='adam', learning_rate=config['learning_rate']),
            objective='policy_gradient',
            reward_estimation=dict(horizon=1)
        )

    def decide_action(self, state):
        """ Décide de l'action à prendre basée sur l'état actuel en utilisant Dueling DQN """
        action = self.agent.act(states=state)
        return action

    def update_policy(self, reward):
        """ Met à jour la politique de l'agent basée sur la rétroaction reçue """
        self.agent.observe(terminal=False, reward=reward)

    def reset(self):
        """ Réinitialise l'agent pour un nouvel épisode """
        self.agent.reset()
        
    def handle_wake_up(self, current_time):
        super().handle_wake_up(current_time)

        
        


