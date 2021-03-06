# This example is set up based on the example provided by Google Research
# https://github.com/google-research/football/blob/master/gfootball/examples/run_ppo2.py
#
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import numpy as np
import tensorflow as tf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from gym import wrappers
from datetime import datetime
import time



import os

from stable_baselines.sac.policies import MlpPolicy
from stable_baselines.sac.policies import FeedForwardPolicy
from stable_baselines import SAC
import baselines.common.tf_util as U


np.random.seed(19)

# config the RLGC Java Sever
java_port = 25034
jar_file = '/lib/RLGCJavaServer0.87.jar'


a = os.path.abspath(os.path.dirname(__file__))
repo_path = a[:-7]

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

jar_path = repo_path + jar_file

case_files_array =list()

case_files_array.append(repo_path + '/testData/IEEE39/IEEE39bus_multiloads_xfmr4_smallX_v30.raw')
case_files_array.append(repo_path + '/testData/IEEE39/IEEE39bus_3AC.dyr')

dyn_config_file = repo_path + '/testData/IEEE39/json/IEEE39_dyn_config.json'
# use the configuration file for continuous action space
rl_config_file = repo_path + '/testData/IEEE39/json/IEEE39_RL_loadShedding_3motor_continuous.json'


storedData = "./storedData"

savedModel= "./trainedModels"
model_name = "IEEE39_multistep_obs11_randftd3_randbus3_3motor2action_prenull"

def callback(lcl, glb):

    if lcl['t'] > 0:
        step_rewards.append(lcl['episode_rewards'])
     #  step_actions.append(lcl['action'])
     #   step_observations.append(lcl['obs'])
     #   step_status.append(lcl['done'])
     #   step_starttime.append(lcl['starttime'])
     #   step_durationtime.append(lcl['durationtime'])
        if lcl['t'] % 499 == 0:
            U.save_state(model_file)

# Custom MLP policy of two layers of size 256 each
class CustomSACPolicy(FeedForwardPolicy):
    def __init__(self, *args, **kwargs):
        super(CustomSACPolicy, self).__init__(*args, **kwargs,
                                           layers=[256, 256],
                                           layer_norm=False,
                                           feature_extraction="mlp")



def train(learning_rate, env, model_path):
    
    tf.reset_default_graph()    # to avoid the conflict the existnat parameters, but not suggested for reuse parameters


    # default policy is MlpPolicy
    model = SAC(CustomSACPolicy, env, verbose=1,seed=10, n_cpu_tf_sess=16)
    model.learn(total_timesteps=500000, log_interval=1000)
    model.save("sac_ieee39_loadshedding")

    #print("Saving final model to power_model_multistep_581_585_lr_%s.pkl" % (str(learning_rate)))
    #ddpg.save(savedModel + "/" + model_name + "_lr_%s_100w.pkl" % (str(learning_rate)))
#aa._act_params


#tf.reset_default_graph()    # to avoid the conflict the existnat parameters, but not suggested for reuse parameters
step_rewards = list()
step_actions = list()
step_observations = list()
step_status = list()
step_starttime = list()
step_durationtime = list()

check_pt_dir = "./PowerGridModels"
if not os.path.exists(check_pt_dir):
    os.makedirs(check_pt_dir)

model_file = os.path.join(check_pt_dir, "gridmodel")


import time
start = time.time()
dataname = "multistep_obs11_randftd3_randbus3_3motor_continuous_prenull_100w"

from PowerDynSimEnvDef_v5 import PowerDynSimEnv
env = PowerDynSimEnv(case_files_array,dyn_config_file,rl_config_file,jar_path,java_port)

#for ll in [0.0001, 0.0005, 0.00005]:
for ll in [0.00005]:
    step_rewards = list()
    step_actions = list()
    step_observations = list()
    step_status = list()
    step_starttime = list()
    step_durationtime = list()

    env.reset()

    #model_path = "./previous_model/IEEE39_multistep_p150_3motor3action_prenull_008_lr_0.0001_30w.pkl"
    model_path = None

    train(ll, env, model_path)

    env.close_connection()

    np.save(os.path.join(storedData, "step_rewards_lr_%s_" % str(ll) + dataname), np.array(step_rewards))
    np.save(os.path.join(storedData, "step_actions_lr_%s_" % str(ll) + dataname), np.array(step_actions))
    np.save(os.path.join(storedData, "step_observations_lr_%s_" % str(ll) + dataname), np.array(step_observations))
    np.save(os.path.join(storedData, "step_status_lr_%s_" % str(ll) + dataname), np.array(step_status))
    np.save(os.path.join(storedData, "step_starttime_lr_%s_" % str(ll) + dataname), np.array(step_starttime))
    np.save(os.path.join(storedData, "step_durationtime_lr_%s_" % str(ll) + dataname), np.array(step_durationtime))


end = time.time()

print("total running time is %s" % (str(end - start)))


#np.save(os.path.join(storedData, "step_rewards_t"), np.array(step_rewards))
#np.save(os.path.join(storedData, "step_actions_t"), np.array(step_actions))
#np.save(os.path.join(storedData, "step_observations_t"), np.array(step_observations))
#np.save(os.path.join(storedData, "step_status_t"), np.array(step_status))
#np.save(os.path.join(storedData, "step_starttime_t"), np.array(step_starttime))
#np.save(os.path.join(storedData, "step_durationtime_t"), np.array(step_durationtime))

print("Finished!!")

def test():
    act = ddpg.load("power_model.pkl")
    done = False


    #for i in range(1):
    obs, done = env._validate(1,8,1.0,0.585), False
    episode_rew = 0
    actions = list()
    while not done:
        #env.render()
        action = act(obs[None])[0]
        #obs, rew, done, _ = env.step(act(obs[None])[0])
        obs, rew, done, _ = env.step(action)
        episode_rew += rew
    print("Episode reward", episode_rew)

    return actions
