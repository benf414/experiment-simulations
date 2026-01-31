import numpy as np
import pandas as pd

from scipy.stats import ttest_ind

class experiment:
    def __init__(self,
                 pre_c_user_sessions,
                 post_c_user_sessions, 
                 pre_t_user_sessions, 
                 post_t_user_sessions, 
                 t_test_n: int, 
                 t_test_cuped_n: int, 
                 seq_test_n: int, 
                 seq_test_cuped_n: int,
                 cuped_theta: float
):
        """
        Creates an experiment object.
        Sessions must be broken into 4 measurements per pre and post experiment period.
        
        Args:
            pre_c_user_sessions (array): pre-experiment data for control group
            post_c_user_sessions (array): post-experiment data for control group
            pre_t_user_sessions (array): pre-experiment data for treatment group
            post_t_user_sessions (array): post-experiment data for treatment group
            t_test_n: required sample size for t-test
            t_test_cuped_n: required sample size for t-test with CUPED
            seq_test_n: required sample size for group sequential test
            seq_test_cuped_n: required sample size for group sequential test with CUPED
            cuped_theta: estimated theta to use for CUPED adjustment
        """
        self.pre_c_user_sessions = pre_c_user_sessions
        self.post_c_user_sessions = post_c_user_sessions
        self.pre_t_user_sessions = pre_t_user_sessions
        self.post_t_user_sessions = post_t_user_sessions
        self.t_test_n = t_test_n
        self.t_test_cuped_n = t_test_cuped_n
        self.seq_test_n = seq_test_n
        self.seq_test_cuped_n = seq_test_cuped_n
        self.cuped_theta = cuped_theta
        self.results = {}

        self._ttest_c_sessions = None
        self._ttest_t_sessions = None
        self._ttest_cuped_c_sessions = None
        self._ttest_cuped_c_cov = None
        self._ttest_cuped_t_sessions = None
        self._ttest_cuped_t_cov = None

        self._seq_c_sessions = None
        self._seq_t_sessions = None
        self._seq_cuped_c_sessions = None
        self._seq_cuped_c_cov = None
        self._seq_cuped_t_sessions = None
        self._seq_cuped_t_cov = None

        self._groups_created = 0
        self._entries_created = 0
        self._entry_data_created = 0

    def create_test_groups(self):
        """
        Creates test groups for the experiment.
        """
        assert len(self.pre_c_user_sessions) >= max(self.t_test_n, self.t_test_cuped_n, self.seq_test_n, self.seq_test_cuped_n), "Not enough pre-experiment control users for required sample"
        assert len(self.post_c_user_sessions) >= max(self.t_test_n, self.t_test_cuped_n, self.seq_test_n, self.seq_test_cuped_n), "Not enough post-experiment control users for required sample"
        assert len(self.pre_t_user_sessions) >= max(self.t_test_n, self.t_test_cuped_n, self.seq_test_n, self.seq_test_cuped_n), "Not enough pre-experiment treatment users for required sample"
        assert len(self.post_t_user_sessions) >= max(self.t_test_n, self.t_test_cuped_n, self.seq_test_n, self.seq_test_cuped_n), "Not enough post-experiment treatment users for required sample"

        df_pre_c_user_sessions = pd.DataFrame(self.pre_c_user_sessions)
        df_post_c_user_sessions = pd.DataFrame(self.post_c_user_sessions)
        df_pre_t_user_sessions = pd.DataFrame(self.pre_t_user_sessions)
        df_post_t_user_sessions = pd.DataFrame(self.post_t_user_sessions)

        df_pre_c_user_sessions['user_id'] = range(len(df_pre_c_user_sessions))
        df_post_c_user_sessions['user_id'] = range(len(df_post_c_user_sessions))
        df_pre_t_user_sessions['user_id'] = range(len(df_pre_t_user_sessions))
        df_post_t_user_sessions['user_id'] = range(len(df_post_t_user_sessions))

        self._ttest_c_sessions = df_post_c_user_sessions.sample(n=self.t_test_n, ignore_index=True)
        self._ttest_t_sessions = df_post_t_user_sessions.sample(n=self.t_test_n, ignore_index=True)
        self._ttest_cuped_c_sessions = df_post_c_user_sessions.sample(n=self.t_test_cuped_n, ignore_index=True)
        self._ttest_cuped_t_sessions = df_post_t_user_sessions.sample(n=self.t_test_cuped_n, ignore_index=True)
        self._ttest_cuped_c_cov = df_pre_c_user_sessions[df_pre_c_user_sessions['user_id'].isin(self._ttest_cuped_c_sessions['user_id'])]
        self._ttest_cuped_t_cov = df_pre_t_user_sessions[df_pre_t_user_sessions['user_id'].isin(self._ttest_cuped_t_sessions['user_id'])]

        self._seq_c_sessions = df_post_c_user_sessions.sample(n=self.seq_test_n, ignore_index=True)
        self._seq_t_sessions = df_post_t_user_sessions.sample(n=self.seq_test_n, ignore_index=True)
        self._seq_cuped_c_sessions = df_post_c_user_sessions.sample(n=self.seq_test_cuped_n, ignore_index=True)
        self._seq_cuped_t_sessions = df_post_t_user_sessions.sample(n=self.seq_test_cuped_n, ignore_index=True)
        self._seq_cuped_c_cov = df_pre_c_user_sessions[df_pre_c_user_sessions['user_id'].isin(self._seq_cuped_c_sessions['user_id'])]
        self._seq_cuped_t_cov = df_pre_t_user_sessions[df_pre_t_user_sessions['user_id'].isin(self._seq_cuped_t_sessions['user_id'])]

        self._groups_created = 1
    
    def create_test_entries(self):
        """
       Creates entry periods for the users.
       Assumes equal entries for each period.
        """
        if self._groups_created == 0:
            print("You must first create test groups via .create_test_groups()")
            return

        #T-test entries
        ttest_c_n = len(self._ttest_c_sessions)
        ttest_c_entries = np.tile([1, 2, 3, 4], ttest_c_n // 4)
        if ttest_c_n % 4 > 0:
            ttest_c_entries = np.concatenate([ttest_c_entries, np.arange(1, ttest_c_n % 4 + 1)])
        np.random.shuffle(ttest_c_entries)
        self._ttest_c_sessions['period_entry'] = ttest_c_entries

        ttest_t_n = len(self._ttest_t_sessions)
        ttest_t_entries = np.tile([1, 2, 3, 4], ttest_t_n // 4)
        if ttest_t_n % 4 > 0:
            ttest_t_entries = np.concatenate([ttest_t_entries, np.arange(1, ttest_t_n % 4 + 1)])
        np.random.shuffle(ttest_t_entries)
        self._ttest_t_sessions['period_entry'] = ttest_t_entries

        #T-test CUPED entries
        ttest_cuped_c_n = len(self._ttest_cuped_c_sessions)
        ttest_cuped_c_entries = np.tile([1, 2, 3, 4], ttest_cuped_c_n // 4)
        if ttest_cuped_c_n % 4 > 0:
            ttest_cuped_c_entries = np.concatenate([ttest_cuped_c_entries, np.arange(1, ttest_cuped_c_n % 4 + 1)])
        np.random.shuffle(ttest_cuped_c_entries)
        self._ttest_cuped_c_sessions['period_entry'] = ttest_cuped_c_entries

        ttest_cuped_t_n = len(self._ttest_cuped_t_sessions)
        ttest_cuped_t_entries = np.tile([1, 2, 3, 4], ttest_cuped_t_n // 4)
        if ttest_cuped_t_n % 4 > 0:
            ttest_cuped_t_entries = np.concatenate([ttest_cuped_t_entries, np.arange(1, ttest_cuped_t_n % 4 + 1)])
        np.random.shuffle(ttest_cuped_t_entries)
        self._ttest_cuped_t_sessions['period_entry'] = ttest_cuped_t_entries

        self._ttest_cuped_c_cov = self._ttest_cuped_c_cov.merge(self._ttest_cuped_c_sessions[['user_id', 'period_entry']], on='user_id', how='left')
        self._ttest_cuped_t_cov = self._ttest_cuped_t_cov.merge(self._ttest_cuped_t_sessions[['user_id', 'period_entry']], on='user_id', how='left')

        #Sequential test entries
        seq_c_n = len(self._seq_c_sessions)
        seq_c_entries = np.tile([1, 2, 3, 4], seq_c_n // 4)
        if seq_c_n % 4 > 0:
            seq_c_entries = np.concatenate([seq_c_entries, np.arange(1, seq_c_n % 4 + 1)])
        np.random.shuffle(seq_c_entries)
        self._seq_c_sessions['period_entry'] = seq_c_entries

        seq_t_n = len(self._seq_t_sessions)
        seq_t_entries = np.tile([1, 2, 3, 4], seq_t_n // 4)
        if seq_t_n % 4 > 0:
            seq_t_entries = np.concatenate([seq_t_entries, np.arange(1, seq_t_n % 4 + 1)])
        np.random.shuffle(seq_t_entries)
        self._seq_t_sessions['period_entry'] = seq_t_entries

        #Sequential CUPED test entries
        seq_cuped_c_n = len(self._seq_cuped_c_sessions)
        seq_cuped_c_entries = np.tile([1, 2, 3, 4], seq_cuped_c_n // 4)
        if seq_cuped_c_n % 4 > 0:
            seq_cuped_c_entries = np.concatenate([seq_cuped_c_entries, np.arange(1, seq_cuped_c_n % 4 + 1)])
        np.random.shuffle(seq_cuped_c_entries)
        self._seq_cuped_c_sessions['period_entry'] = seq_cuped_c_entries

        seq_cuped_t_n = len(self._seq_cuped_t_sessions)
        seq_cuped_t_entries = np.tile([1, 2, 3, 4], seq_cuped_t_n // 4)
        if seq_cuped_t_n % 4 > 0:
            seq_cuped_t_entries = np.concatenate([seq_cuped_t_entries, np.arange(1, seq_cuped_t_n % 4 + 1)])
        np.random.shuffle(seq_cuped_t_entries)
        self._seq_cuped_t_sessions['period_entry'] = seq_cuped_t_entries

        self._seq_cuped_c_cov = self._seq_cuped_c_cov.merge(self._seq_cuped_c_sessions[['user_id', 'period_entry']], on='user_id', how='left')
        self._seq_cuped_t_cov = self._seq_cuped_t_cov.merge(self._seq_cuped_t_sessions[['user_id', 'period_entry']], on='user_id', how='left')

        self._entries_created = 1

    def expand_test_entry_data(table, period, inverse=False):
        """
        Sums sessions for a period based on entry.
        """
        if not inverse:
            table[f'period{period}_total_sessions'] = np.select(
                [
                    table['period_entry'] == 1,
                    table['period_entry'] == 2,
                    table['period_entry'] == 3,
                    table['period_entry'] == 4,
                    table['period_entry'] > period
                ],
               [
                    sum([table[i] for i in range(period)]),
                    sum([table[i] for i in range(1, period)]),
                    sum([table[i] for i in range(2, period)]),
                    sum([table[i] for i in range(3, period)]),
                    0
                ]
            )
        else:
            table[f'period{period}_total_sessions'] = np.select(
                [
                    table['period_entry'] == 1,
                    table['period_entry'] == 2,
                    table['period_entry'] == 3,
                    table['period_entry'] == 4,
                    table['period_entry'] > period
                ],
               [
                    sum([table[i] for i in range(4 - period, 4)]),
                    sum([table[i] for i in range(5 - period, 4)]),
                    sum([table[i] for i in range(min(4, 6 - period), 4)]),
                    sum([table[i] for i in range(min(4, 7 - period), 4)]),
                    0
                ]
            ) 
        
        return table

    
    def create_test_entry_data(self):
        """
        Creates data based on user entries.
        """
        if self._entries_created == 0:
            print("You must first create test entries via .create_test_entries()")
            return
        
        self._ttest_c_sessions = experiment.expand_test_entry_data(self._ttest_c_sessions, period=4)
        self._ttest_t_sessions = experiment.expand_test_entry_data(self._ttest_t_sessions, period=4)
        
        self._ttest_cuped_c_sessions = experiment.expand_test_entry_data(self._ttest_cuped_c_sessions, period=4)
        self._ttest_cuped_t_sessions = experiment.expand_test_entry_data(self._ttest_cuped_t_sessions, period=4)
        self._ttest_cuped_c_cov = experiment.expand_test_entry_data(self._ttest_cuped_c_cov, period=4, inverse=True)
        self._ttest_cuped_t_cov = experiment.expand_test_entry_data(self._ttest_cuped_t_cov, period=4, inverse=True)

        self._seq_c_sessions = experiment.expand_test_entry_data(self._seq_c_sessions, period=4)
        self._seq_c_sessions = experiment.expand_test_entry_data(self._seq_c_sessions, period=3)
        self._seq_c_sessions = experiment.expand_test_entry_data(self._seq_c_sessions, period=2)
        self._seq_c_sessions = experiment.expand_test_entry_data(self._seq_c_sessions, period=1)
        self._seq_t_sessions = experiment.expand_test_entry_data(self._seq_t_sessions, period=4)
        self._seq_t_sessions = experiment.expand_test_entry_data(self._seq_t_sessions, period=3)
        self._seq_t_sessions = experiment.expand_test_entry_data(self._seq_t_sessions, period=2)
        self._seq_t_sessions = experiment.expand_test_entry_data(self._seq_t_sessions, period=1)

        self._seq_cuped_c_sessions = experiment.expand_test_entry_data(self._seq_cuped_c_sessions, period=4)
        self._seq_cuped_c_sessions = experiment.expand_test_entry_data(self._seq_cuped_c_sessions, period=3)
        self._seq_cuped_c_sessions = experiment.expand_test_entry_data(self._seq_cuped_c_sessions, period=2)
        self._seq_cuped_c_sessions = experiment.expand_test_entry_data(self._seq_cuped_c_sessions, period=1)
        self._seq_cuped_t_sessions = experiment.expand_test_entry_data(self._seq_cuped_t_sessions, period=4)
        self._seq_cuped_t_sessions = experiment.expand_test_entry_data(self._seq_cuped_t_sessions, period=3)
        self._seq_cuped_t_sessions = experiment.expand_test_entry_data(self._seq_cuped_t_sessions, period=2)
        self._seq_cuped_t_sessions = experiment.expand_test_entry_data(self._seq_cuped_t_sessions, period=1)
        self._seq_cuped_c_cov = experiment.expand_test_entry_data(self._seq_cuped_c_cov, period=4, inverse=True)
        self._seq_cuped_c_cov = experiment.expand_test_entry_data(self._seq_cuped_c_cov, period=3, inverse=True)
        self._seq_cuped_c_cov = experiment.expand_test_entry_data(self._seq_cuped_c_cov, period=2, inverse=True)
        self._seq_cuped_c_cov = experiment.expand_test_entry_data(self._seq_cuped_c_cov, period=1, inverse=True)
        self._seq_cuped_t_cov = experiment.expand_test_entry_data(self._seq_cuped_t_cov, period=4, inverse=True)
        self._seq_cuped_t_cov = experiment.expand_test_entry_data(self._seq_cuped_t_cov, period=3, inverse=True)
        self._seq_cuped_t_cov = experiment.expand_test_entry_data(self._seq_cuped_t_cov, period=2, inverse=True)
        self._seq_cuped_t_cov = experiment.expand_test_entry_data(self._seq_cuped_t_cov, period=1, inverse=True)

        self._entry_data_created = 1
    
    def run_experiment(self):
        """
        Runs experiment.
        """
        if self._entry_data_created == 0:
            print("You must first create test entry data via .create_test_entry_data()")
            return
        
        #T-test analysis
        _, ttest_p_value = ttest_ind(self._ttest_c_sessions['period4_total_sessions'], self._ttest_t_sessions['period4_total_sessions'])
        if ttest_p_value < 0.05:
            ttest_stat_sig = 1
        else:
            ttest_stat_sig = 0
        
        self.results['ttest'] = {
            'sample_size': len(self._ttest_c_sessions) + len(self._ttest_t_sessions),
            'p_value': round(float(ttest_p_value), 3),
            'significance': ttest_stat_sig
        }

        #T-test CUPED analysis
        self._ttest_cuped_c_sessions = self._ttest_cuped_c_sessions.merge(self._ttest_cuped_c_cov[['user_id', 'period4_total_sessions']], on='user_id', how='left', suffixes=('', '_cov'))
        self._ttest_cuped_t_sessions = self._ttest_cuped_t_sessions.merge(self._ttest_cuped_t_cov[['user_id', 'period4_total_sessions']], on='user_id', how='left', suffixes=('', '_cov'))
        
        ttest_cuped_pre_sessions = pd.concat([self._ttest_cuped_c_cov['period4_total_sessions'], self._ttest_cuped_t_cov['period4_total_sessions']], ignore_index=True)
        ttest_cov_mean = ttest_cuped_pre_sessions.mean()
        
        self._ttest_cuped_c_sessions['sessions_cuped'] = self._ttest_cuped_c_sessions['period4_total_sessions'] - self.cuped_theta * (self._ttest_cuped_c_sessions['period4_total_sessions_cov'] - ttest_cov_mean)
        self._ttest_cuped_t_sessions['sessions_cuped'] = self._ttest_cuped_t_sessions['period4_total_sessions'] - self.cuped_theta * (self._ttest_cuped_t_sessions['period4_total_sessions_cov'] - ttest_cov_mean)
       
        _, ttest_cuped_p_value = ttest_ind(self._ttest_cuped_c_sessions['sessions_cuped'], self._ttest_cuped_t_sessions['sessions_cuped'])
        if ttest_cuped_p_value < 0.05:
            ttest_cuped_stat_sig = 1
        else:
            ttest_cuped_stat_sig = 0
        
        self.results['ttest_cuped'] = {
            'sample_size': len(self._ttest_cuped_c_sessions) + len(self._ttest_cuped_t_sessions),
            'p_value': round(float(ttest_cuped_p_value), 3),
            'significance': ttest_cuped_stat_sig
        }
        
        #Sequential test analysis
        
        #Using O'Brien-Fleming method
        seq_p_values = [.001, .0039, .0185, .045]

        seq_look = 1
        seq_finished = False
        while not seq_finished:
            seq_c_filtered = self._seq_c_sessions[self._seq_c_sessions['period_entry'] <= seq_look]
            seq_t_filtered = self._seq_t_sessions[self._seq_t_sessions['period_entry'] <= seq_look]

            session_col_nm = f'period{seq_look}_total_sessions'
            _, ttest_seq_p_value = ttest_ind(seq_c_filtered[session_col_nm], seq_t_filtered[session_col_nm])
            
            if ttest_seq_p_value < seq_p_values[seq_look-1]:
                self.results['seq'] = {
                    'sample_size': len(seq_c_filtered) + len(seq_t_filtered),
                    'p_value': round(float(ttest_seq_p_value), 3),
                    'significance': 1
                }
                seq_finished = True
            elif seq_look == 4:
                self.results['seq'] = {
                    'sample_size': len(seq_c_filtered) + len(seq_t_filtered),
                    'p_value': round(float(ttest_seq_p_value), 3),
                    'significance': 0
                }
                seq_finished = True
            else:
                seq_look += 1
        
        #Sequential test CUPED analysis
        seq_look = 1
        seq_finished = False
        while not seq_finished:
            seq_cuped_c_filtered = self._seq_cuped_c_sessions[self._seq_cuped_c_sessions['period_entry'] <= seq_look]
            seq_cuped_t_filtered = self._seq_cuped_t_sessions[self._seq_cuped_t_sessions['period_entry'] <= seq_look]
            seq_cuped_c_cov = self._seq_cuped_c_cov[self._seq_cuped_c_cov['period_entry'] <= seq_look]
            seq_cuped_t_cov = self._seq_cuped_t_cov[self._seq_cuped_t_cov['period_entry'] <= seq_look]

            session_col_nm = f'period{seq_look}_total_sessions'

            seq_cuped_c_filtered = seq_cuped_c_filtered.merge(seq_cuped_c_cov[['user_id', session_col_nm]], on='user_id', how='left', suffixes=('', '_cov'))
            seq_cuped_t_filtered = seq_cuped_t_filtered.merge(seq_cuped_t_cov[['user_id', session_col_nm]], on='user_id', how='left', suffixes=('', '_cov'))

            #estimating theta using control only since treatment effects are heterogenous
            seq_cuped_pre_sessions = pd.concat([seq_cuped_c_cov[session_col_nm], seq_cuped_t_cov[session_col_nm]], ignore_index=True)
            seq_cov_mean = seq_cuped_pre_sessions.mean()

            seq_cuped_c_filtered[f'{session_col_nm}_cuped'] = seq_cuped_c_filtered[session_col_nm] - self.cuped_theta * (seq_cuped_c_filtered[f'{session_col_nm}_cov'] - seq_cov_mean)
            seq_cuped_t_filtered[f'{session_col_nm}_cuped'] = seq_cuped_t_filtered[session_col_nm] - self.cuped_theta * (seq_cuped_t_filtered[f'{session_col_nm}_cov'] - seq_cov_mean)
            _, ttest_seq_cuped_p_value = ttest_ind(seq_cuped_c_filtered[f'{session_col_nm}_cuped'], seq_cuped_t_filtered[f'{session_col_nm}_cuped'])
            
            if ttest_seq_cuped_p_value < seq_p_values[seq_look-1]:
                self.results['seq_cuped'] = {
                    'sample_size': len(seq_cuped_c_filtered) + len(seq_cuped_t_filtered),
                    'p_value': round(float(ttest_seq_cuped_p_value), 3),
                    'significance': 1
                }
                seq_finished = True
            elif seq_look == 4:
                self.results['seq_cuped'] = {
                    'sample_size': len(seq_cuped_c_filtered) + len(seq_cuped_t_filtered),
                    'p_value': round(float(ttest_seq_cuped_p_value),3),
                    'significance': 0
                }
                seq_finished = True
            else:
                seq_look += 1
