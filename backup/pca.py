import numpy as np

def pca(image_matrix,m,n):
    mean_vec = np.mean(image_matrix, axis=1)		
    mean_subtract_vec=(image_matrix.T-mean_vec).T		
    cov_m = np.dot(mean_subtract_vec,mean_subtract_vec.T)/(image_matrix.shape[1]) 
		
    eig_vals, eig_vecs = np.linalg.eig(cov_m)
    eig_pairs =[(np.abs(eig_vals[i]), eig_vecs[:,i]) for i in range(len(eig_vals))]
    eig_pairs.sort()
    eig_pairs.reverse()
		
    pc=np.array([np.dot(eig_pairs[i][1],mean_subtract_vec).reshape(m,n) for i in range(0,3)])
    return eig_pairs,pc
