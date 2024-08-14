import numpy as np
import pandas as pd
from model import KnowledgeModel
import matplotlib.pyplot as plt
import os


class Simulator():
    """A simulator to run multiple knowledge models."""
    
    def __init__(self, N, S, T, graph, nx_params, sharingMode, shareTimeLimit, delay, singleSource, samePartition):
        self.N = N
        self.S = S
        self.T = T
        self.graph = graph
        self.nx_params = nx_params
        self.mode = sharingMode
        self.delay = delay
        self.singleSource = singleSource
        self.samePartition = samePartition
        self.shareTimeLimit = shareTimeLimit

    def runModel(self, network):
        """Run network model for T timesteps and return logs."""

        # create model
        model = KnowledgeModel(network=network,
                               sharingMode=self.mode,
                               sharetime=self.shareTimeLimit,
                               delay=self.delay,
                               singleSource=self.singleSource,
                               samePartition=self.samePartition)

        # run model
        for t in range(self.T - 1):
            model.step()

        return model.logs()

    def runSimulation(self, save, experiment, subexperiment, network_name, nx_params, export_csv=True):
        """Run model over S simulations and return aggregate logs."""

        num_neutral_per_agent = np.empty(shape=(self.S))
        num_Method_A_per_agent = np.empty(shape=(self.S))
        num_Method_B_per_agent = np.empty(shape=(self.S))
        num_Method_C_per_agent = np.empty(shape=(self.S))
        neutral_per_timestep = np.empty(shape=(self.S, self.T))
        Method_A_per_timestep = np.empty(shape=(self.S, self.T))
        Method_B_per_timestep = np.empty(shape=(self.S, self.T))
        Method_C_per_timestep = np.empty(shape=(self.S, self.T))
    
        directory = "./Output/" + experiment 
        name = network_name + '_' + '_'.join(['{}={}'.format(k, v) for k, v in nx_params.items()])

        ratio_logs = []

        for s in range(self.S):
            # run model
            network = self.graph(**self.nx_params)  # generate network from graph and params
            logs = self.runModel(network=network)
            df_belief = pd.DataFrame.from_dict(logs[0])

            if save:  # write raw data to output directory
                if not os.path.exists(directory):
                    os.makedirs(directory)

                out = pd.DataFrame(index=[x for x in range(self.T)], columns=['s', 't']+[x for x in range(self.N)])
                out.iloc[:, 0] = np.repeat(s+1, repeats=self.T)  # vector of timesteps  # simulation number
                out.iloc[:, 1] = np.linspace(start=1, stop=self.T, num=self.T, dtype=int)  # timestep number
                out.iloc[:, 2:self.N+2] = df_belief.values

            # Calculate ratios
            neutral_ratio = np.mean(df_belief.values == 0, axis=1)
            Method_A_ratio = np.mean(df_belief.values == 1, axis=1)
            Method_B_ratio = np.mean(df_belief.values == 2, axis=1)
            Method_C_ratio = np.mean(df_belief.values == 3, axis=1)

            for t in range(self.T):
                ratio_logs.append([s + 1, t + 1, neutral_ratio[t], Method_A_ratio[t], Method_B_ratio[t], Method_C_ratio[t]])

            # eval output
            num_neutral_per_agent[s] = np.mean(np.sum(df_belief.values == 0, axis=0))
            num_Method_A_per_agent[s] = np.mean(np.sum(df_belief.values == 1, axis=0))
            num_Method_B_per_agent[s] = np.mean(np.sum(df_belief.values == 2, axis=0))
            num_Method_C_per_agent[s] = np.mean(np.sum(df_belief.values == 3, axis=0))
            neutral_per_timestep[s, :] = neutral_ratio
            Method_A_per_timestep[s, :] = Method_A_ratio
            Method_B_per_timestep[s, :] = Method_B_ratio
            Method_C_per_timestep[s, :] = Method_C_ratio

        # Create a common filename base
        filename_base = "/N={N}-T={T}-S={S}-shr={shr}-dly={dly}-{name}".format(
            N=self.N, T=self.T, S=self.S, shr=self.shareTimeLimit, dly=self.delay, name=name)

        # Save ratio logs to a CSV file if export_csv is True
        if export_csv:
            ratio_df = pd.DataFrame(ratio_logs, columns=['Simulation', 'Timestep', 'Neutral', 'Method_A', 'Method_B', 'Method_C'])
            csv_directory = directory
            if not os.path.exists(csv_directory):
                os.makedirs(csv_directory)
            csv_filename = csv_directory + filename_base + ".csv"
            ratio_df.to_csv(csv_filename, index=False)

        # aggregate beliefs over time
        neutral_per_agent_avg = np.mean(num_neutral_per_agent)
        neutral_per_agent_sd = np.std(num_neutral_per_agent)
        Method_A_per_agent_avg = np.mean(num_Method_A_per_agent)
        Method_A_per_agent_sd = np.std(num_Method_A_per_agent)
        Method_B_per_agent_avg = np.mean(num_Method_B_per_agent)
        Method_B_per_agent_sd = np.std(num_Method_B_per_agent)
        Method_C_per_agent_avg = np.mean(num_Method_C_per_agent)
        Method_C_per_agent_sd = np.std(num_Method_C_per_agent)
        frac_neutral_per_timestep = np.mean(neutral_per_timestep, axis=0)
        frac_neutral_per_timestep_sd = np.std(neutral_per_timestep, axis=0)
        frac_Method_A_per_timestep = np.mean(Method_A_per_timestep, axis=0)
        frac_Method_A_per_timestep_sd = np.std(Method_A_per_timestep, axis=0)
        frac_Method_B_per_timestep = np.mean(Method_B_per_timestep, axis=0)
        frac_Method_B_per_timestep_sd = np.std(Method_B_per_timestep, axis=0)
        frac_Method_C_per_timestep = np.mean(Method_C_per_timestep, axis=0)
        frac_Method_C_per_timestep_sd = np.std(Method_C_per_timestep, axis=0)

        # aggregate final belief distributions
        neutral_dist = neutral_per_timestep[:, self.T-1]
        Method_A_dist = Method_A_per_timestep[:, self.T-1]
        Method_B_dist = Method_B_per_timestep[:, self.T-1]
        Method_C_dist = Method_C_per_timestep[:, self.T-1]

        # bundle aggregated output
        avg_per_agent = (neutral_per_agent_avg, Method_A_per_agent_avg, Method_B_per_agent_avg, Method_C_per_agent_avg)
        sd_per_agent = (neutral_per_agent_sd, Method_A_per_agent_sd, Method_B_per_agent_sd, Method_C_per_agent_sd)
        frac_belief_mean = (frac_neutral_per_timestep, frac_Method_A_per_timestep, frac_Method_B_per_timestep, frac_Method_C_per_timestep)
        frac_belief_sd = (frac_neutral_per_timestep_sd, frac_Method_A_per_timestep_sd, frac_Method_B_per_timestep_sd, frac_Method_C_per_timestep_sd)
        belief_dist = (neutral_dist, Method_A_dist, Method_B_dist, Method_C_dist)

        return avg_per_agent, sd_per_agent, frac_belief_mean, frac_belief_sd, belief_dist

    def visFinalBeliefDistributions(self, belief_dist, data, experiment, subexperiment, network_name, nx_params, save):
        """Plot belief distributions on final time step over all simulations."""

        avg_agent_beliefs, sd_agent_beliefs, _, _ = data
        avg_neutral, avg_Method_A, avg_Method_B, avg_Method_C = avg_agent_beliefs
        sd_neutral, sd_Method_A, sd_Method_B, sd_Method_C = sd_agent_beliefs
        neutral_dist, Method_A_dist, Method_B_dist, Method_C_dist = belief_dist
        ranges = np.linspace(start=0, stop=1, num=100)

        fig, axes = plt.subplots(4, 1, figsize=(10, 12))
    
        axes[0].hist(neutral_dist, bins=ranges)
        axes[0].set_ylim(0, self.S)
        axes[0].set_ylabel("Neutral", fontsize=14)
    
        axes[1].hist(Method_A_dist, bins=ranges, color='blue')
        axes[1].set_ylim(0, self.S)
        axes[1].set_ylabel("Method A", fontsize=14)
    
        axes[2].hist(Method_B_dist, bins=ranges, color='orange')
        axes[2].set_ylim(0, self.S)
        axes[2].set_ylabel("Method B", fontsize=14)
    
        axes[3].hist(Method_C_dist, bins=ranges, color='green')
        axes[3].set_ylim(0, self.S)
        axes[3].set_xlabel("Fraction of population holding belief at time T", fontsize=14)
        axes[3].set_ylabel("Method C", fontsize=14)

        for ax in axes:
            ax.tick_params(axis='both', which='major', labelsize=14)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.3f}'))
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
    
        if save:  # write plot to output directory
            directory = "./Output/" + experiment + "/hist/"
            if not os.path.exists(directory):
                os.makedirs(directory)
            network_name = network_name + '_' + '_'.join(['{}={}'.format(k, v) for k, v in nx_params.items()])
            filename_base = "/N={N}-T={T}-S={S}-shr={shr}-dly={dly}-{name}".format(
                N=self.N, T=self.T, S=self.S, shr=self.shareTimeLimit, dly=self.delay, name=network_name,
                avg_n=round(avg_neutral, 1), avg_f=round(avg_Method_A, 1), avg_r=round(avg_Method_B, 1), avg_a=round(avg_Method_C, 1), sd_n=round(sd_neutral, 1), sd_f=round(sd_Method_A, 1), sd_r=round(sd_Method_B, 1), sd_a=round(sd_Method_C, 1))
            filename = filename_base + ".png"
            plt.savefig(directory + filename, bbox_inches="tight", format='png', dpi=900)

        plt.tight_layout()
        plt.show()

    def visBeliefsOverTime(self, data, experiment, subexperiment, network_name, nx_params, save, plot_sd=False):
        """Plot data and output to file."""

        # unpack aggregate data
        avg_num, sd_num, frac_belief_mean, frac_belief_sd = data
        avg_neutral, avg_Method_A, avg_Method_B, avg_Method_C = avg_num
        sd_neutral, sd_Method_A, sd_Method_B, sd_Method_C = sd_num
        neutral_mean, Method_A_mean, Method_B_mean, Method_C_mean = frac_belief_mean
        neutral_sd, Method_A_sd, Method_B_sd, Method_C_sd = frac_belief_sd

        alpha = 0.5
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(range(self.T), neutral_mean, label="Neutral", color="grey", ls="-", linewidth=2)
        ax.plot(range(self.T), Method_A_mean, label="Method A", color="blue", ls="-", linewidth=2)
        ax.plot(range(self.T), Method_B_mean, label="Method B", color="orange", ls="-", linewidth=2)
        ax.plot(range(self.T), Method_C_mean, label="Method C", color="green", ls="-", linewidth=2)
        if plot_sd:
            ax.plot(range(self.T), Method_A_mean + Method_A_sd, color="blue", ls="--", alpha=alpha)
            ax.plot(range(self.T), Method_A_mean - Method_A_sd, color="blue", ls="--", alpha=alpha)
            ax.plot(range(self.T), neutral_mean + neutral_sd, color="grey", ls="--", alpha=alpha)
            ax.plot(range(self.T), neutral_mean - neutral_sd, color="grey", ls="--", alpha=alpha)
            ax.plot(range(self.T), Method_B_mean + Method_B_sd, color="orange", ls="--", alpha=alpha)
            ax.plot(range(self.T), Method_B_mean - Method_B_sd, color="orange", ls="--", alpha=alpha)
            ax.plot(range(self.T), Method_C_mean + Method_C_sd, color="green", ls="--", alpha=alpha)
            ax.plot(range(self.T), Method_C_mean - Method_C_sd, color="green", ls="--", alpha=alpha)
        ax.set_xlim(0, self.T)
        ax.set_ylim(0, 1.11)
        ax.set_xlabel("Time", fontsize=14)
        ax.set_ylabel("Ratio of population belief", fontsize=14)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=4, fancybox=False, fontsize=14, frameon=False)
        ax.tick_params(axis='both', which='major', labelsize=14)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.3f}'))

        # Remove the upper and right spines
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)

        if save:  # write plot to output directory
            directory = "./Output/" + experiment
            directory += "/sd" if plot_sd else ""  # create subfolder for sd plots
            if not os.path.exists(directory):
                os.makedirs(directory)
            network_name = network_name + '_' + '_'.join(['{}={}'.format(k, v) for k, v in nx_params.items()])
            filename_base = "/N={N}-T={T}-S={S}-shr={shr}-dly={dly}-{name}-3P".format(
                N=self.N, T=self.T, S=self.S, shr=self.shareTimeLimit, dly=self.delay, name=network_name,
                avg_n=round(avg_neutral, 1), avg_f=round(avg_Method_A, 1), avg_r=round(avg_Method_B, 1), avg_a=round(avg_Method_C, 1), sd_n=round(sd_neutral, 1), sd_f=round(sd_Method_A, 1), sd_r=round(sd_Method_B, 1), sd_a=round(sd_Method_C, 1), sd=("-sd" if plot_sd else ""))
            filename = filename_base + ".png"
            plt.savefig(directory + filename, bbox_inches="tight", format='png', dpi=900)

        plt.tight_layout()
        plt.show()
