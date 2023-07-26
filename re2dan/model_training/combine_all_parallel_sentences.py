import gzip
import glob

files = glob.glob("./parallel-sentences/*.tsv.gz")
try:
    files.remove('./parallel-sentences/all_parallel_data_train.tsv.gz')
    files.remove('./parallel-sentences/all_parallel_data_dev.tsv.gz')
except:
    print("No combined files found - no need to skip them")

train_data = []
dev_data = []
for file in files:
    with gzip.open(file, 'rt', encoding='utf-8') as f:
        lines = f.readlines()
        print(file, len(lines))
        train_data.extend(lines[len(lines)//50:])
        dev_data.extend(lines[:len(lines)//50])

print("Train data", len(train_data))
print("Dev data", len(dev_data))

with open("./parallel-sentences/all_parallel_data_train.tsv", 'w') as f:
    f.writelines(train_data)
with open("./parallel-sentences/all_parallel_data_dev.tsv", 'w') as f:
    f.writelines(dev_data)

with open("./parallel-sentences/all_parallel_data_train.tsv", 'rb') as f_in, gzip.open("./parallel-sentences/all_parallel_data_train.tsv.gz", 'wb') as f_out:
    f_out.writelines(f_in)
with open("./parallel-sentences/all_parallel_data_dev.tsv", 'rb') as f_in, gzip.open("./parallel-sentences/all_parallel_data_dev.tsv.gz", 'wb') as f_out:
    f_out.writelines(f_in)


