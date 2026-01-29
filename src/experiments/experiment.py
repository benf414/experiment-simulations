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
):
        """
        Creates an experiment object.
        Sessions must be broken into 4 measurements per pre and post experiment period.
        Sequential tests use 4 looks assigning significance threshold to .001, .0039, .0185, .045
        
        Args:
            pre_c_user_sessions (array): pre-experiment data for control group
            post_c_user_sessions (array): post-experiment data for control group
            pre_t_user_sessions (array): pre-experiment data for treatment group
            post_t_user_sessions (array): post-experiment data for treatment group
            t_test_n: required sample size for t-test
            t_test_cuped_n: required sample size for t-test with CUPED
            seq_test_n: required sample size for group sequential test
            seq_test_cuped_n: required sample size for group sequential test with CUPED
        """
        self.pre_c_user_sessions = pre_c_user_sessions
        self.post_c_user_sessions = post_c_user_sessions
        self.pre_t_user_sessions = pre_t_user_sessions
        self.post_t_user_sessions = post_t_user_sessions
        self.t_test_n = t_test_n
        self.t_test_cuped_n = t_test_cuped_n
        self.seq_test_n = seq_test_n
        self.seq_test_cuped_n = seq_test_cuped_n
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

    def create_test_groups(self):
        """
        Creates test groups for the experiment.
        """
        df_pre_c_user_sessions = pd.DataFrame(self.pre_c_user_sessions)
        df_post_c_user_sessions = pd.DataFrame(self.post_c_user_sessions)
        df_pre_t_user_sessions = pd.DataFrame(self.pre_t_user_sessions)
        df_post_t_user_sessions = pd.DataFrame(self.post_t_user_sessions)

        df_pre_c_user_sessions['user_id'] = range(len(df_pre_c_user_sessions))
        df_post_c_user_sessions['user_id'] = range(len(df_post_c_user_sessions))
        df_pre_t_user_sessions['user_id'] = range(len(df_pre_t_user_sessions))
        df_post_t_user_sessions['user_id'] = range(len(df_post_t_user_sessions))

        self._ttest_c_sessions = df_post_c_user_sessions.sample(n=self.t_test_n)
        self._ttest_t_sessions = df_post_t_user_sessions.sample(n=self.t_test_n)
        self._ttest_cuped_c_sessions = df_post_c_user_sessions.sample(n=self.t_test_cuped_n)
        self._ttest_cuped_t_sessions = df_post_t_user_sessions.sample(n=self.t_test_cuped_n)
        self._ttest_cuped_c_cov = df_pre_c_user_sessions[df_pre_c_user_sessions['user_id'].isin(self._ttest_cuped_c_sessions['user_id'])]
        self._ttest_cuped_t_cov = df_pre_t_user_sessions[df_pre_t_user_sessions['user_id'].isin(self._ttest_cuped_t_sessions['user_id'])]

        self._seq_c_sessions = df_post_c_user_sessions.sample(n=self.seq_test_n)
        self._seq_t_sessions = df_post_t_user_sessions.sample(n=self.seq_test_n)
        self._seq_cuped_c_sessions = df_post_c_user_sessions.sample(n=self.seq_test_cuped_n)
        self._seq_cuped_t_sessions = df_post_t_user_sessions.sample(n=self.seq_test_cuped_n)
        self._seq_cuped_c_cov = df_pre_c_user_sessions[df_pre_c_user_sessions['user_id'].isin(self._seq_cuped_c_sessions['user_id'])]
        self._seq_cuped_t_cov = df_pre_t_user_sessions[df_pre_t_user_sessions['user_id'].isin(self._seq_cuped_t_sessions['user_id'])]

        self._groups_created = 1
    
    def create_test_entries(self):
        """
       Creates entry periods for the users.
        """
        if self._groups_created == 0:
            print("You must first create test groups via .create_test_groups()")
            return

        #T-test entries
        ttest_c_entries = np.tile([1, 2, 3, 4], len(self._ttest_c_sessions) // 4)
        if len(self._ttest_c_sessions) % 4 > 0:
            ttest_c_entries = np.concatenate([ttest_c_entries, np.arange(1, len(self._ttest_c_sessions) % 4 + 1)])
        np.random.shuffle(ttest_c_entries)
        self._ttest_c_sessions['period_entry'] = ttest_c_entries

        ttest_t_entries = np.tile([1, 2, 3, 4], len(self._ttest_t_sessions) // 4)
        if len(self._ttest_t_sessions) % 4 > 0:
            ttest_t_entries = np.concatenate([ttest_t_entries, np.arange(1, len(self._ttest_t_sessions) % 4 + 1)])
        np.random.shuffle(ttest_t_entries)
        self._ttest_t_sessions['period_entry'] = ttest_t_entries

        #T-test CUPED entries
        ttest_cuped_c_entries = np.tile([1, 2, 3, 4], len(self._ttest_cuped_c_sessions) // 4)
        if len(self._ttest_cuped_c_sessions) % 4 > 0:
            ttest_cuped_c_entries = np.concatenate([ttest_cuped_c_entries, np.arange(1, len(self._ttest_cuped_c_sessions) % 4 + 1)])
        np.random.shuffle(ttest_cuped_c_entries)
        self._ttest_cuped_c_sessions['period_entry'] = ttest_cuped_c_entries

        ttest_cuped_t_entries = np.tile([1, 2, 3, 4], len(self._ttest_cuped_t_sessions) // 4)
        if len(self._ttest_cuped_t_sessions) % 4 > 0:
            ttest_cuped_t_entries = np.concatenate([ttest_cuped_t_entries, np.arange(1, len(self._ttest_cuped_t_sessions) % 4 + 1)])
        np.random.shuffle(ttest_cuped_t_entries)
        self._ttest_cuped_t_sessions['period_entry'] = ttest_cuped_t_entries

        self._ttest_cuped_c_cov = self._ttest_cuped_c_cov.merge(self._ttest_cuped_c_sessions[['user_id', 'period_entry']], on='user_id', how='left')
        self._ttest_cuped_t_cov = self._ttest_cuped_t_cov.merge(self._ttest_cuped_t_sessions[['user_id', 'period_entry']], on='user_id', how='left')

        #Sequential test entries
        seq_c_entries = np.tile([1, 2, 3, 4], len(self._seq_c_sessions) // 4)
        if len(self._seq_c_sessions) % 4 > 0:
            seq_c_entries = np.concatenate([seq_c_entries, np.arange(1, len(self._seq_c_sessions) % 4 + 1)])
        np.random.shuffle(seq_c_entries)
        self._seq_c_sessions['period_entry'] = seq_c_entries

        seq_t_entries = np.tile([1, 2, 3, 4], len(self._seq_t_sessions) // 4)
        if len(self._seq_t_sessions) % 4 > 0:
            seq_t_entries = np.concatenate([seq_t_entries, np.arange(1, len(self._seq_t_sessions) % 4 + 1)])
        np.random.shuffle(seq_t_entries)
        self._seq_t_sessions['period_entry'] = seq_t_entries

        #Sequential CUPED test entries
        seq_cuped_c_entries = np.tile([1, 2, 3, 4], len(self._seq_cuped_c_sessions) // 4)
        if len(self._seq_cuped_c_sessions) % 4 > 0:
            seq_cuped_c_entries = np.concatenate([seq_cuped_c_entries, np.arange(1, len(self._seq_cuped_c_sessions) % 4 + 1)])
        np.random.shuffle(seq_cuped_c_entries)
        self._seq_cuped_c_sessions['period_entry'] = seq_cuped_c_entries

        seq_cuped_t_entries = np.tile([1, 2, 3, 4], len(self._seq_cuped_t_sessions) // 4)
        if len(self._seq_cuped_t_sessions) % 4 > 0:
            seq_cuped_t_entries = np.concatenate([seq_cuped_t_entries, np.arange(1, len(self._seq_cuped_t_sessions) % 4 + 1)])
        np.random.shuffle(seq_cuped_t_entries)
        self._seq_cuped_t_sessions['period_entry'] = seq_cuped_t_entries

        self._seq_cuped_c_cov = self._seq_cuped_c_cov.merge(self._seq_cuped_c_sessions[['user_id', 'period_entry']], on='user_id', how='left')
        self._seq_cuped_t_cov = self._seq_cuped_t_cov.merge(self._seq_cuped_t_sessions[['user_id', 'period_entry']], on='user_id', how='left')

        self._entries_created = 1

    def run_experiment(self):
        """
        Runs experiment.
        """
        if self._entries_created == 0:
            print("You must first create test entries via .create_test_entries()")
            return
        
        #T-test analysis
        self._ttest_c_sessions['total_sessions'] = self._ttest_c_sessions[0] + self._ttest_c_sessions[1] + self._ttest_c_sessions[2] + self._ttest_c_sessions[3]
        self._ttest_t_sessions['total_sessions'] = self._ttest_t_sessions[0] + self._ttest_t_sessions[1] + self._ttest_t_sessions[2] + self._ttest_t_sessions[3]

        _, ttest_p_value = ttest_ind(self._ttest_c_sessions['total_sessions'], self._ttest_t_sessions['total_sessions'])
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
        self._ttest_cuped_c_sessions['total_sessions'] = self._ttest_cuped_c_sessions[0] + self._ttest_cuped_c_sessions[1] + self._ttest_cuped_c_sessions[2] + self._ttest_cuped_c_sessions[3]
        self._ttest_cuped_t_sessions['total_sessions'] = self._ttest_cuped_t_sessions[0] + self._ttest_cuped_t_sessions[1] + self._ttest_cuped_t_sessions[2] + self._ttest_cuped_t_sessions[3]
        self._ttest_cuped_c_cov['total_sessions'] = self._ttest_cuped_c_cov[0] + self._ttest_cuped_c_cov[1] + self._ttest_cuped_c_cov[2] + self._ttest_cuped_c_cov[3]
        self._ttest_cuped_t_cov['total_sessions'] = self._ttest_cuped_t_cov[0] + self._ttest_cuped_t_cov[1] + self._ttest_cuped_t_cov[2] + self._ttest_cuped_t_cov[3]
        
        self._ttest_cuped_c_sessions = self._ttest_cuped_c_sessions.merge(self._ttest_cuped_c_cov[['user_id', 'total_sessions']], on='user_id', how='left', suffixes=('', '_cov'))
        self._ttest_cuped_t_sessions = self._ttest_cuped_t_sessions.merge(self._ttest_cuped_t_cov[['user_id', 'total_sessions']], on='user_id', how='left', suffixes=('', '_cov'))
        
        ttest_cuped_pre_sessions = pd.concat([self._ttest_cuped_c_cov['total_sessions'], self._ttest_cuped_t_cov['total_sessions']], ignore_index=True)
        ttest_cuped_post_sessions = pd.concat([self._ttest_cuped_c_sessions['total_sessions'], self._ttest_cuped_t_sessions['total_sessions']], ignore_index=True)
        cuped_covar = np.cov(ttest_cuped_pre_sessions, ttest_cuped_post_sessions)[0, 1]
        cov_mean = ttest_cuped_pre_sessions.mean()
        
        self._ttest_cuped_c_sessions['sessions_cuped'] = self._ttest_cuped_c_sessions['total_sessions'] - cuped_covar * (self._ttest_cuped_c_sessions['total_sessions_cov'] - cov_mean)
        self._ttest_cuped_t_sessions['sessions_cuped'] = self._ttest_cuped_t_sessions['total_sessions'] - cuped_covar * (self._ttest_cuped_t_sessions['total_sessions_cov'] - cov_mean)
        
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
        seq_p_values = [.001, .0039, .0185, .045]

        #Create control looks
        for n in range(4):
            self._seq_c_sessions[f'look{n+1}_sessions'] = 0

        seq_c_p1_sessions = self._seq_c_sessions[self._seq_c_sessions['period_entry'] == 1]
        seq_c_p2_sessions = self._seq_c_sessions[self._seq_c_sessions['period_entry'] == 2]
        seq_c_p3_sessions = self._seq_c_sessions[self._seq_c_sessions['period_entry'] == 3]
        seq_c_p4_sessions = self._seq_c_sessions[self._seq_c_sessions['period_entry'] == 4]

        seq_c_p1_sessions['look1_sessions'] = seq_c_p1_sessions[0]
        seq_c_p1_sessions['look2_sessions'] = seq_c_p1_sessions[0] + seq_c_p1_sessions[1]
        seq_c_p1_sessions['look3_sessions'] = seq_c_p1_sessions[0] + seq_c_p1_sessions[1] + seq_c_p1_sessions[2]
        seq_c_p1_sessions['look4_sessions'] = seq_c_p1_sessions[0] + seq_c_p1_sessions[1] + seq_c_p1_sessions[2] + seq_c_p1_sessions[3]

        seq_c_p2_sessions['look2_sessions'] = seq_c_p2_sessions[1]
        seq_c_p2_sessions['look3_sessions'] = seq_c_p2_sessions[1] + seq_c_p2_sessions[2]
        seq_c_p2_sessions['look4_sessions'] = seq_c_p2_sessions[1] + seq_c_p2_sessions[2] + seq_c_p2_sessions[3]

        seq_c_p3_sessions['look3_sessions'] = seq_c_p3_sessions[2]
        seq_c_p3_sessions['look4_sessions'] = seq_c_p3_sessions[2] + seq_c_p3_sessions[3]

        seq_c_p4_sessions['look4_sessions'] = seq_c_p4_sessions[3]

        seq_c_sessions_adj = pd.concat([seq_c_p1_sessions, seq_c_p2_sessions, seq_c_p3_sessions, seq_c_p4_sessions], ignore_index=True)
        
        #Create treatment looks
        for n in range(4):
            self._seq_t_sessions[f'look{n+1}_sessions'] = 0

        seq_t_p1_sessions = self._seq_t_sessions[self._seq_t_sessions['period_entry'] == 1]
        seq_t_p2_sessions = self._seq_t_sessions[self._seq_t_sessions['period_entry'] == 2]
        seq_t_p3_sessions = self._seq_t_sessions[self._seq_t_sessions['period_entry'] == 3]
        seq_t_p4_sessions = self._seq_t_sessions[self._seq_t_sessions['period_entry'] == 4]

        seq_t_p1_sessions['look1_sessions'] = seq_t_p1_sessions[0]
        seq_t_p1_sessions['look2_sessions'] = seq_t_p1_sessions[0] + seq_t_p1_sessions[1]
        seq_t_p1_sessions['look3_sessions'] = seq_t_p1_sessions[0] + seq_t_p1_sessions[1] + seq_t_p1_sessions[2]
        seq_t_p1_sessions['look4_sessions'] = seq_t_p1_sessions[0] + seq_t_p1_sessions[1] + seq_t_p1_sessions[2] + seq_t_p1_sessions[3]

        seq_t_p2_sessions['look2_sessions'] = seq_t_p2_sessions[1]
        seq_t_p2_sessions['look3_sessions'] = seq_t_p2_sessions[1] + seq_t_p2_sessions[2]
        seq_t_p2_sessions['look4_sessions'] = seq_t_p2_sessions[1] + seq_t_p2_sessions[2] + seq_t_p2_sessions[3]
        
        seq_t_p3_sessions['look3_sessions'] = seq_t_p3_sessions[2]
        seq_t_p3_sessions['look4_sessions'] = seq_t_p3_sessions[2] + seq_t_p3_sessions[3]

        seq_t_p4_sessions['look4_sessions'] = seq_t_p4_sessions[3]

        seq_t_sessions_adj = pd.concat([seq_t_p1_sessions, seq_t_p2_sessions, seq_t_p3_sessions, seq_t_p4_sessions], ignore_index=True)

        #Simulate the looks
        seq_look = 1
        seq_finished = False
        while not seq_finished:
            seq_c_filtered = seq_c_sessions_adj[seq_c_sessions_adj['period_entry'] <= seq_look]
            seq_t_filtered = seq_t_sessions_adj[seq_t_sessions_adj['period_entry'] <= seq_look]

            session_col_nm = f'look{seq_look}_sessions'
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

        #Create control looks
    
        for n in range(4):
            self._seq_cuped_c_sessions[f'look{n+1}_sessions'] = 0

        seq_cuped_c_p1_sessions = self._seq_cuped_c_sessions[self._seq_cuped_c_sessions['period_entry'] == 1]
        seq_cuped_c_p2_sessions = self._seq_cuped_c_sessions[self._seq_cuped_c_sessions['period_entry'] == 2]
        seq_cuped_c_p3_sessions = self._seq_cuped_c_sessions[self._seq_cuped_c_sessions['period_entry'] == 3]
        seq_cuped_c_p4_sessions = self._seq_cuped_c_sessions[self._seq_cuped_c_sessions['period_entry'] == 4]

        seq_cuped_c_p1_sessions['look1_sessions'] = seq_cuped_c_p1_sessions[0]
        seq_cuped_c_p1_sessions['look2_sessions'] = seq_cuped_c_p1_sessions[0] + seq_cuped_c_p1_sessions[1]
        seq_cuped_c_p1_sessions['look3_sessions'] = seq_cuped_c_p1_sessions[0] + seq_cuped_c_p1_sessions[1] + seq_cuped_c_p1_sessions[2]
        seq_cuped_c_p1_sessions['look4_sessions'] = seq_cuped_c_p1_sessions[0] + seq_cuped_c_p1_sessions[1] + seq_cuped_c_p1_sessions[2] + seq_cuped_c_p1_sessions[3]

        seq_cuped_c_p2_sessions['look2_sessions'] = seq_cuped_c_p2_sessions[1]
        seq_cuped_c_p2_sessions['look3_sessions'] = seq_cuped_c_p2_sessions[1] + seq_cuped_c_p2_sessions[2]
        seq_cuped_c_p2_sessions['look4_sessions'] = seq_cuped_c_p2_sessions[1] + seq_cuped_c_p2_sessions[2] + seq_cuped_c_p2_sessions[3]

        seq_cuped_c_p3_sessions['look3_sessions'] = seq_cuped_c_p3_sessions[2]
        seq_cuped_c_p3_sessions['look4_sessions'] = seq_cuped_c_p3_sessions[2] + seq_cuped_c_p3_sessions[3]

        seq_cuped_c_p4_sessions['look4_sessions'] = seq_cuped_c_p4_sessions[3]
        
        seq_cuped_c_sessions_adj = pd.concat([seq_cuped_c_p1_sessions, seq_cuped_c_p2_sessions, seq_cuped_c_p3_sessions, seq_cuped_c_p4_sessions], ignore_index=True)

        for n in range(4):
            self._seq_cuped_c_cov[f'look{n+1}_sessions'] = 0

        seq_cuped_c_p1_cov = self._seq_cuped_c_cov[self._seq_cuped_c_cov['period_entry'] == 1]
        seq_cuped_c_p2_cov = self._seq_cuped_c_cov[self._seq_cuped_c_cov['period_entry'] == 2]
        seq_cuped_c_p3_cov = self._seq_cuped_c_cov[self._seq_cuped_c_cov['period_entry'] == 3]
        seq_cuped_c_p4_cov = self._seq_cuped_c_cov[self._seq_cuped_c_cov['period_entry'] == 4]

        seq_cuped_c_p1_cov['look1_sessions'] = seq_cuped_c_p1_cov[3]
        seq_cuped_c_p1_cov['look2_sessions'] = seq_cuped_c_p1_cov[3] + seq_cuped_c_p1_cov[2]
        seq_cuped_c_p1_cov['look3_sessions'] = seq_cuped_c_p1_cov[3] + seq_cuped_c_p1_cov[2] + seq_cuped_c_p1_cov[1]
        seq_cuped_c_p1_cov['look4_sessions'] = seq_cuped_c_p1_cov[3] + seq_cuped_c_p1_cov[2] + seq_cuped_c_p1_cov[1] + seq_cuped_c_p1_cov[0]

        seq_cuped_c_p2_cov['look2_sessions'] = seq_cuped_c_p2_cov[2]
        seq_cuped_c_p2_cov['look3_sessions'] = seq_cuped_c_p2_cov[2] + seq_cuped_c_p2_cov[1]
        seq_cuped_c_p2_cov['look4_sessions'] = seq_cuped_c_p2_cov[2] + seq_cuped_c_p2_cov[1] + seq_cuped_c_p2_cov[0]

        seq_cuped_c_p3_cov['look3_sessions'] = seq_cuped_c_p3_cov[1]
        seq_cuped_c_p3_cov['look4_sessions'] = seq_cuped_c_p3_cov[1] + seq_cuped_c_p3_cov[0]

        seq_cuped_c_p4_cov['look4_sessions'] = seq_cuped_c_p4_cov[0]
        
        seq_cuped_c_cov_adj = pd.concat([seq_cuped_c_p1_cov, seq_cuped_c_p2_cov, seq_cuped_c_p3_cov, seq_cuped_c_p4_cov], ignore_index=True)

        #Create treatment looks
        for n in range(4):
            self._seq_cuped_t_sessions[f'look{n+1}_sessions'] = 0

        seq_cuped_t_p1_sessions = self._seq_cuped_t_sessions[self._seq_cuped_t_sessions['period_entry'] == 1]
        seq_cuped_t_p2_sessions = self._seq_cuped_t_sessions[self._seq_cuped_t_sessions['period_entry'] == 2]
        seq_cuped_t_p3_sessions = self._seq_cuped_t_sessions[self._seq_cuped_t_sessions['period_entry'] == 3]
        seq_cuped_t_p4_sessions = self._seq_cuped_t_sessions[self._seq_cuped_t_sessions['period_entry'] == 4]

        seq_cuped_t_p1_sessions['look1_sessions'] = seq_cuped_t_p1_sessions[0]
        seq_cuped_t_p1_sessions['look2_sessions'] = seq_cuped_t_p1_sessions[0] + seq_cuped_t_p1_sessions[1]
        seq_cuped_t_p1_sessions['look3_sessions'] = seq_cuped_t_p1_sessions[0] + seq_cuped_t_p1_sessions[1] + seq_cuped_t_p1_sessions[2]
        seq_cuped_t_p1_sessions['look4_sessions'] = seq_cuped_t_p1_sessions[0] + seq_cuped_t_p1_sessions[1] + seq_cuped_t_p1_sessions[2] + seq_cuped_t_p1_sessions[3]

        seq_cuped_t_p2_sessions['look2_sessions'] = seq_cuped_t_p2_sessions[1]
        seq_cuped_t_p2_sessions['look3_sessions'] = seq_cuped_t_p2_sessions[1] + seq_cuped_t_p2_sessions[2]
        seq_cuped_t_p2_sessions['look4_sessions'] = seq_cuped_t_p2_sessions[1] + seq_cuped_t_p2_sessions[2] + seq_cuped_t_p2_sessions[3]
        
        seq_cuped_t_p3_sessions['look3_sessions'] = seq_cuped_t_p3_sessions[2]
        seq_cuped_t_p3_sessions['look4_sessions'] = seq_cuped_t_p3_sessions[2] + seq_cuped_t_p3_sessions[3]

        seq_cuped_t_p4_sessions['look4_sessions'] = seq_cuped_t_p4_sessions[3]
        
        seq_cuped_t_sessions_adj = pd.concat([seq_cuped_t_p1_sessions, seq_cuped_t_p2_sessions, seq_cuped_t_p3_sessions, seq_cuped_t_p4_sessions], ignore_index=True)

        for n in range(4):
            self._seq_cuped_t_cov[f'look{n+1}_sessions'] = 0

        seq_cuped_t_p1_cov = self._seq_cuped_t_cov[self._seq_cuped_t_cov['period_entry'] == 1]
        seq_cuped_t_p2_cov = self._seq_cuped_t_cov[self._seq_cuped_t_cov['period_entry'] == 2]
        seq_cuped_t_p3_cov = self._seq_cuped_t_cov[self._seq_cuped_t_cov['period_entry'] == 3]
        seq_cuped_t_p4_cov = self._seq_cuped_t_cov[self._seq_cuped_t_cov['period_entry'] == 4]

        seq_cuped_t_p1_cov['look1_sessions'] = seq_cuped_t_p1_cov[3]
        seq_cuped_t_p1_cov['look2_sessions'] = seq_cuped_t_p1_cov[3] + seq_cuped_t_p1_cov[2]
        seq_cuped_t_p1_cov['look3_sessions'] = seq_cuped_t_p1_cov[3] + seq_cuped_t_p1_cov[2] + seq_cuped_t_p1_cov[1]
        seq_cuped_t_p1_cov['look4_sessions'] = seq_cuped_t_p1_cov[3] + seq_cuped_t_p1_cov[2] + seq_cuped_t_p1_cov[1] + seq_cuped_t_p1_cov[0]

        seq_cuped_t_p2_cov['look2_sessions'] = seq_cuped_t_p2_cov[2]
        seq_cuped_t_p2_cov['look3_sessions'] = seq_cuped_t_p2_cov[2] + seq_cuped_t_p2_cov[1]
        seq_cuped_t_p2_cov['look4_sessions'] = seq_cuped_t_p2_cov[2] + seq_cuped_t_p2_cov[1] + seq_cuped_t_p2_cov[0]

        seq_cuped_t_p3_cov['look3_sessions'] = seq_cuped_t_p3_cov[1]
        seq_cuped_t_p3_cov['look4_sessions'] = seq_cuped_t_p3_cov[1] + seq_cuped_t_p3_cov[0]

        seq_cuped_t_p4_cov['look4_sessions'] = seq_cuped_t_p4_cov[0]
        
        seq_cuped_t_cov_adj = pd.concat([seq_cuped_t_p1_cov, seq_cuped_t_p2_cov, seq_cuped_t_p3_cov, seq_cuped_t_p4_cov], ignore_index=True)

        seq_cuped_c_sessions_adj = seq_cuped_c_sessions_adj.merge(seq_cuped_c_cov_adj[['user_id', 'look1_sessions', 'look2_sessions', 'look3_sessions', 'look4_sessions']], on='user_id', how='left', suffixes=('', '_cov'))
        seq_cuped_t_sessions_adj = seq_cuped_t_sessions_adj.merge(seq_cuped_t_cov_adj[['user_id', 'look1_sessions', 'look2_sessions', 'look3_sessions', 'look4_sessions']], on='user_id', how='left', suffixes=('', '_cov'))  

        print(seq_cuped_c_sessions_adj)
        print(seq_cuped_t_sessions_adj)
        
        # Simulate the looks
        seq_look = 1
        seq_finished = False
        while not seq_finished:
            seq_cuped_c_filtered = seq_cuped_c_sessions_adj[seq_cuped_c_sessions_adj['period_entry'] <= seq_look]
            seq_cuped_t_filtered = seq_cuped_t_sessions_adj[seq_cuped_t_sessions_adj['period_entry'] <= seq_look]
            seq_cuped_c_cov = seq_cuped_c_cov_adj[seq_cuped_c_cov_adj['period_entry'] <= seq_look]
            seq_cuped_t_cov = seq_cuped_t_cov_adj[seq_cuped_t_cov_adj['period_entry'] <= seq_look]

            session_col_nm = f'look{seq_look}_sessions'
            seq_cuped_pre_sessions = pd.concat([seq_cuped_c_cov[session_col_nm], seq_cuped_t_cov[session_col_nm]], ignore_index=True)
            seq_cuped_post_sessions = pd.concat([seq_cuped_c_filtered[session_col_nm], seq_cuped_t_filtered[session_col_nm]], ignore_index=True)
            cuped_cov = np.cov(seq_cuped_pre_sessions, seq_cuped_post_sessions)[0, 1]
            cov_mean = seq_cuped_pre_sessions.mean()

            seq_cuped_c_filtered[f'{session_col_nm}_cuped'] = seq_cuped_c_filtered[session_col_nm] - cuped_cov * (seq_cuped_c_filtered[f'{session_col_nm}_cov'] - cov_mean)
            seq_cuped_t_filtered[f'{session_col_nm}_cuped'] = seq_cuped_t_filtered[session_col_nm] - cuped_cov * (seq_cuped_t_filtered[f'{session_col_nm}_cov'] - cov_mean)

            _, ttest_seq_cuped_p_value = ttest_ind(seq_cuped_c_filtered[f'{session_col_nm}_cuped'], seq_cuped_t_filtered[f'{session_col_nm}_cuped'])
            
            fake_dict = {}
            fake_dict[seq_look] = {
                    'sample_size': len(seq_cuped_c_filtered) + len(seq_cuped_t_filtered),
                    'p_value': round(float(ttest_seq_cuped_p_value), 3)
                }
            print(fake_dict)

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







