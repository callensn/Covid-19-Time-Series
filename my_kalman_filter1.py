import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import inv, norm

class KalmanFilter(object):
    def __init__(self,F,Q,H,R,u,one_d=False):
        """
        Initialize the dynamical system models.
        
        Parameters
        ----------
        F : ndarray of shape (n,n)
            The state transition model.
        Q : ndarray of shape (n,n)
            The covariance matrix for the state noise.
        H : ndarray of shape (m,n)
            The observation model.
        R : ndarray of shape (m,m)
            The covariance matric for observation noise.
        u : ndarray of shape (n,)
            The control vector.
        """
        self.one_d = one_d
        self.F = F
        self.Q = Q
        self.H = H
        self.R = R
        self.u = u
    
    def evolve(self,x0,N):
        """
        Compute the first N states and observations generated by the Kalman system.

        Parameters
        ----------
        x0 : ndarray of shape (n,)
            The initial state.
        N : integer
            The number of time steps to evolve.

        Returns
        -------
        states : ndarray of shape (n,N)
            The i-th column gives the i-th state.
        obs : ndarray of shape (m,N)
            The i-th column gives the i-th observation.
        """
        x = [x0]
        z = []
        
        if not self.one_d:
        
            for t in range(N):
                w = np.random.multivariate_normal(np.array([0,0,0,0]), self.Q)
                v = np.random.multivariate_normal(np.array([0,0]), self.R)
                x1 = self.F@x0 + self.u + w
                z1 = self.H@x0 + v
                
                x.append(x1)
                z.append(z1)
                
                x0 = x1
        else:
            for t in range(N):
                w = np.random.normal(0, self.Q)
                v = np.random.normal(0, self.R)
                x1 = self.F*x0 + self.u + w
                z1 = self.H*x0 + v
                
                x.append(x1)
                z.append(z1)
                
        return x, z     

    def estimate(self,x0,P0,z, return_norms = False):
        """
        Compute the state estimates using the kalman filter.

        Parameters
        ----------
        x0 : ndarray of shape (n,)
            The initial state estimate.
        P0 : ndarray of shape (n,n)
            The initial error covariance matrix.
        z : ndarray of shape(m,N)
            Sequence of N observations (each column is an observation).

        Returns
        -------
        out : ndarray of shape (n,N)
            Sequence of state estimates (each column is an estimate).
        norms: list of floats of length N
            Gives the norm of the error matrix for each estimate.
        """
        N = len(z)
        out = []
        P = []
        
        if not self.one_d:
            I = np.eye(len(P0))
            for i in range(N):
                #Predict step
                new_x = self.F@x0 + self.u
                new_P = self.F@P0@self.F.T + self.Q
                
                #Update step
                y_t = z[i] - self.H@new_x
                Sk = self.H@new_P@self.H.T + self.R
                Kk = new_P@self.H.T@(inv(Sk))
                final_x = new_x + Kk@y_t
                final_P = (I - Kk@self.H)@new_P
                
                out.append(final_x)
                P.append(final_P)
                
                x0 = final_x
                P0 = final_P
                
        else:
            for i in range(N):
                new_x = self.F*x0 + self.u
                new_P = (self.F**2)*P0 + self.Q
                
                y_t = z[i] - self.H*new_x
                Sk = (self.H**2)*new_P + self.R
                Kk = new_P*self.H*(1/Sk)
                final_x = new_x + Kk*y_t
                final_P = (1 - Kk*self.H)*new_P
                
                out.append(final_x)
                P.append(final_P)
                
                x0 = final_x
                P0 = final_P
                
        return out, P
            
            
            
    
    def predict(self,x,k):
        """
        Predict the next k states in the absence of observations.

        Parameters
        ----------
        x : ndarray of shape (n,)
            The current state estimate.
        k : integer
            The number of states to predict.

        Returns
        -------
        out : ndarray of shape (n,k)
            The next k predicted states.
        """
        new_x = [x]
        
        if not self.one_d:
            for i in range(k-1):
                new_x.append(self.F@new_x[-1] + self.u)
        
            
            return np.array(new_x).reshape((k,len(x)))
        
        else:
            for i in range(k-1):
                new_x.append(self.F*new_x[-1] + self.u)
                
            return new_x
    
    def rewind(self,x,k):
        """
        Predict the states from time 0 through k-1 in the absence of observations.
    
        Parameters
        ----------
        x : ndarray of shape (n,)
            The state estimate at time k.
        k : integer
            The current time step.
    
        Returns
        -------
        out : ndarray of shape (n,k)
            The predicted states from time 0 up through k-1 (in that order).
        """
        new_x = [x]
        
        if not self.one_d:
            for i in range(k-1):
                new_x.append(inv(self.F)@(new_x[-1] - self.u))
    
            return np.array(new_x).reshape((k, len(x)))
        
        else:
            for i in range(k-1):
                new_x.append((1/self.F)*(new_x[-1] - self.u))
            return new_x

def problem2():
    """ 
    Instantiate and retrun a KalmanFilter object with the transition and observation 
    models F and H, along with the control vector u, corresponding to the 
    projectile. Assume that the noise covariances are given by
    Q = 0.1 ?? I4
    R = 5000 ?? I2.
    
    Return the KalmanFilter Object
    """
    Q = np.eye(4)*.1
    R = 5000*np.eye(2)
    F = np.array([[1,0,.1,0], [0,1,0,.1], [0,0,1,0], [0,0,0,1]])
    H = np.array([[1,0,0,0], [0,1,0,0]])
    u = np.array([0,0,0,-0.98])
    new_filter = KalmanFilter(F, Q, H, R, u) 
    
    #x, z = new_filter.evolve(np.array([0,0,300,600]), 1250)
    return new_filter
    
"""x, z = problem2()
new_z = np.array(z).reshape((1250,2))
new_x = np.array(x).reshape((1250,4))
plt.subplot(1,2,1)
plt.plot(new_x[:,0], new_x[:,1])
plt.subplot(1,2,2)
plt.plot(new_z[:,0], new_z[:,1], color="red")
plt.tight_layout()
plt.show()"""

def problem5(plot=True):
    """
    Calculate an initial state estimate xb200. Using the initial state estimate, 
    P200 and your Kalman Filter, compute the next 600 state estimates. 
    Plot these state estimates as a smooth green
    curve together with the radar observations (as red dots) and the entire
    true state sequence (as blue curve).
    """
    KF = problem2()
    x, z = KF.evolve(np.array([0,0,300,600]), 1250)
    new_z = np.array(z).reshape((1250,2))
    new_x = np.array(x).reshape((1251,4))
    z_slice = new_z[200:800]
    
    z_initial = z_slice[0:9]
    z_diff = np.diff(z_initial, axis=0)/.1
    avg = np.mean(z_diff, axis=0)
    
    x0 = np.array([z_slice[0][0], z_slice[0][1], avg[0], avg[1]])
    P0 = 10**6 * KF.Q
    x_final, P_final = KF.estimate(x0, P0, z_slice)
    
    if plot:
        x0 = np.array(x).reshape((1251,4))
        x_final = np.array(x_final).reshape((600,4))
        z_ = np.array(z_slice).reshape((600,2))
        plt.subplot(121)
        plt.plot(x0[:,0], x0[:,1], color="blue", lw=.5)
        plt.scatter(z_[:,0], z_[:,1], color="red", s=.5)
        plt.plot(x_final[:,0], x_final[:,1], color="green")
        plt.title("Big Picture")
        plt.subplot(122)
        plt.plot(x0[:,0], x0[:,1], color="blue", lw=.5)
        plt.scatter(z_[:,0], z_[:,1], color="red", s=.5)
        plt.plot(x_final[:,0], x_final[:,1], color="green")
        plt.title("Zoomed In")
        plt.xlim(7400,9200)
        plt.ylim(11800, 13600)
        plt.tight_layout()
        plt.show()
    return x_final, P_final, new_x, z_slice, KF
    
#problem5()


def problem7():
    """
    Using the final state estimate xb800 that you obtained in Problem 5, 
    predict the future states of the projectile until it hits the ground. 
    Plot the actual state sequence together with the predicted state sequence 
    (as a yellow curve), and observe how near the prediction is to the actual 
    point of impact. Y
    """    
    xf, pf, x0, zs, KF = problem5(False) 
    initial_x = xf[-1]
    preds = KF.predict(initial_x, 450)
    plt.subplot(121)
    plt.plot(x0[:,0], x0[:,1], color="blue")
    plt.plot(preds[:,0], preds[:,1], color="yellow", lw=1.25)
    plt.title("Actual vs. Prediction")
    plt.subplot(122)
    plt.plot(x0[:,0], x0[:,1], color="blue")
    plt.plot(preds[:,0], preds[:,1], color="yellow", lw=1.25)
    plt.xlim(35000, 36000)
    plt.ylim(0,100)
    plt.title("Zoomed In")
    plt.show()

#problem7()


def problem9():
    """
    Using your state estimate xb250, predict the point of origin of the 
    projectile along with all states leading up to time step 250. 
    Plot these predicted states (in cyan) together with the original state 
    sequence. Repeat the prediction starting with xb600. 
    """
    xf, pf, x0, zs, KF = problem5(False) 
    initial_x = xf[50]
    initial_x_2 = xf[400]
    preds = KF.rewind(initial_x, 250)
    preds2 = KF.rewind(initial_x_2, 600)
    plt.subplot(121)
    plt.plot(x0[:,0], x0[:,1], color="blue")
    plt.plot(preds[:,0], preds[:,1], color="yellow", lw=1.25)
    plt.title("Starting at 250")
    
    plt.subplot(122)
    plt.plot(x0[:,0], x0[:,1], color="blue")
    plt.plot(preds2[:,0], preds2[:,1], color="yellow", lw=1.25)
    plt.title("Starting at 600")
    plt.show()
#problem9()