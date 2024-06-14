import os

import pandas as pd
import glob
from sklearn.isotonic import IsotonicRegression

path = os.getcwd()
csv_files = glob.glob(os.path.join(path + '/data', "part*"))

df = pd.read_csv(csv_files[0], header=None, names = ['cvr_score_int', 'pred_cvr', 'cnt', 'gt_cvr'])
df.sort_values('pred_cvr', inplace=True)
X = df['pred_cvr'].values
y = df['gt_cvr'].values
pcopc_inverse = y / (X + 1e-8)
sw = df['cnt'].values
# print样本
with pd.option_context('display.max_rows', None, 'display.max_columns', None,'display.precision', 8,):
	print(df)

X_eval = [i * 0.0001 for i in range(1, 10001)]
y_hat = IsotonicRegression(out_of_bounds='clip').fit(X, y, sw).predict(X_eval)
ratio = [3 if i >= 3 else i for i in y_hat / X_eval]


k_res = []
b_res = []
for i in range(10000):
	x_pre = 0.0 if i == 0 else X_eval[i-1]
	y_pre = 0.0 if i == 0 else y_hat[i-1]

	k = (y_hat[i] - y_pre) / (X_eval[i] - x_pre)
	b = y_hat[i] - k * X_eval[i]
	k_res.append(k)
	b_res.append(b)

# print 保序回归结果
df2 = pd.DataFrame(
	{
		"cvr": pd.Series(X_eval),
		"iso_reg_cvr": pd.Series(y_hat),
		"ratio": pd.Series(ratio)
	}
)
with pd.option_context('display.max_rows', None,'display.max_columns', None,'display.precision', 8,):
	print(df2)

# 结果写txt
with open("cvr_calibration_dict_1.txt", 'w+') as f:
	for i in range(len(X_eval)):
		line = ''
		line = line + str(i) + '\t'
		line = line + '{value_oneof_case:9,val_map:{entries_map:{rate:{value_oneof_case:4,val_double:' +str(k_res[i]) +  '},bias:{value_oneof_case:4,val_double:' + str(b_res[i]) + '}}}}'
		line = line + '\n'
		f.write(line)


import matplotlib.pyplot as plt
# 历史代码，画各种散点图
fig, axes = plt.subplots(1,3)
axes[0].scatter(X, y)
axes[0].set_xlabel("predict_ctr")
axes[0].set_ylabel("ground_truth_ctr")

axes[1].scatter(X, pcopc_inverse)
axes[1].set_xlabel("predict_ctr")
axes[1].set_ylabel("pcopc inverse")

axes[2].scatter(X_eval, y_hat)
axes[2].set_xlabel("predict_ctr")
axes[2].set_ylabel("iso_regression res")

plt.show()
