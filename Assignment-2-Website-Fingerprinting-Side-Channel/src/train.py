import os
import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, Subset
from sklearn.metrics import classification_report
from sklearn.model_selection import StratifiedShuffleSplit

# Configuration
DATASET_PATH = "2005048_data.json"
MODELS_DIR = "saved_models"
BATCH_SIZE = 64
EPOCHS = 50
LEARNING_RATE = 1e-4
TRAIN_SPLIT = 0.8
HIDDEN_SIZE = 128

# Ensure models directory exists
os.makedirs(MODELS_DIR, exist_ok=True)

class FingerprintClassifier(nn.Module):
    """Basic CNN for fingerprint classification."""
    def __init__(self, input_size, hidden_size, num_classes):
        super().__init__()
        self.conv1 = nn.Conv1d(1, 32, kernel_size=5, stride=2, padding=2)
        self.pool1 = nn.MaxPool1d(2)
        self.conv2 = nn.Conv1d(32, 64, kernel_size=5, stride=1, padding=2)
        self.pool2 = nn.MaxPool1d(2)
        conv_out = input_size // 8
        self.fc_input = conv_out * 64
        self.fc1 = nn.Linear(self.fc_input, hidden_size)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(hidden_size, num_classes)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = x.unsqueeze(1)
        x = self.relu(self.conv1(x))
        x = self.pool1(x)
        x = self.relu(self.conv2(x))
        x = self.pool2(x)
        x = x.view(-1, self.fc_input)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        return self.fc2(x)

class ComplexFingerprintClassifier(nn.Module):
    """Deeper CNN with batch-norm and extra conv layer."""
    def __init__(self, input_size, hidden_size, num_classes):
        super().__init__()
        self.conv1 = nn.Conv1d(1, 32, 5, padding=2)
        self.bn1 = nn.BatchNorm1d(32)
        self.pool1 = nn.MaxPool1d(2)
        self.conv2 = nn.Conv1d(32, 64, 3, padding=1)
        self.bn2 = nn.BatchNorm1d(64)
        self.pool2 = nn.MaxPool1d(2)
        self.conv3 = nn.Conv1d(64, 128, 3, padding=1)
        self.bn3 = nn.BatchNorm1d(128)
        self.pool3 = nn.MaxPool1d(2)
        conv_out = input_size // 8
        self.fc_input = conv_out * 128
        self.fc1 = nn.Linear(self.fc_input, hidden_size*2)
        self.bn4 = nn.BatchNorm1d(hidden_size*2)
        self.dropout1 = nn.Dropout(0.5)
        self.fc2 = nn.Linear(hidden_size*2, hidden_size)
        self.bn5 = nn.BatchNorm1d(hidden_size)
        self.dropout2 = nn.Dropout(0.3)
        self.fc3 = nn.Linear(hidden_size, num_classes)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = x.unsqueeze(1)
        x = self.relu(self.bn1(self.conv1(x)))
        x = self.pool1(x)
        x = self.relu(self.bn2(self.conv2(x)))
        x = self.pool2(x)
        x = self.relu(self.bn3(self.conv3(x)))
        x = self.pool3(x)
        x = x.view(-1, self.fc_input)
        x = self.relu(self.bn4(self.fc1(x)))
        x = self.dropout1(x)
        x = self.relu(self.bn5(self.fc2(x)))
        x = self.dropout2(x)
        return self.fc3(x)

class ResidualBlock1D(nn.Module):
    def __init__(self, in_ch, out_ch, stride=1, downsample=None):
        super().__init__()
        self.conv1 = nn.Conv1d(in_ch, out_ch, 3, stride=stride, padding=1)
        self.bn1 = nn.BatchNorm1d(out_ch)
        self.relu = nn.ReLU()
        self.conv2 = nn.Conv1d(out_ch, out_ch, 3, padding=1)
        self.bn2 = nn.BatchNorm1d(out_ch)
        self.downsample = downsample

    def forward(self, x):
        identity = x
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        if self.downsample:
            identity = self.downsample(x)
        out += identity
        return self.relu(out)

class ResNet1DClassifier(nn.Module):
    """ResNet-style classifier with 1D convolutions."""
    def __init__(self, input_size, num_classes, layers=[2,2,2], base_ch=64):
        super().__init__()
        self.in_ch = base_ch
        self.conv = nn.Conv1d(1, base_ch, 7, stride=2, padding=3)
        self.bn = nn.BatchNorm1d(base_ch)
        self.relu = nn.ReLU()
        self.maxpool = nn.MaxPool1d(3, stride=2, padding=1)
        self.layer1 = self._make_layer(base_ch, layers[0])
        self.layer2 = self._make_layer(base_ch*2, layers[1], stride=2)
        self.layer3 = self._make_layer(base_ch*4, layers[2], stride=2)
        self.avgpool = nn.AdaptiveAvgPool1d(1)
        self.fc = nn.Linear(base_ch*4, num_classes)

    def _make_layer(self, out_ch, blocks, stride=1):
        down = None
        if stride!=1 or self.in_ch!=out_ch:
            down = nn.Sequential(
                nn.Conv1d(self.in_ch, out_ch, 1, stride=stride),
                nn.BatchNorm1d(out_ch)
            )
        layers = [ResidualBlock1D(self.in_ch, out_ch, stride, down)]
        self.in_ch = out_ch
        for _ in range(1, blocks):
            layers.append(ResidualBlock1D(out_ch, out_ch))
        return nn.Sequential(*layers)

    def forward(self, x):
        x = x.unsqueeze(1)
        x = self.relu(self.bn(self.conv(x)))
        x = self.maxpool(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.avgpool(x)
        x = x.squeeze(-1)
        return self.fc(x)

class LSTMClassifier(nn.Module):
    """Bidirectional LSTM classifier."""
    def __init__(self, input_size, hidden_size, num_classes, num_layers=2, bidir=True, dropout=0.5):
        super().__init__()
        self.lstm = nn.LSTM(1, hidden_size, num_layers, batch_first=True,
                            bidirectional=bidir, dropout=dropout)
        fc_in = hidden_size * (2 if bidir else 1)
        self.fc1 = nn.Linear(fc_in, hidden_size)
        self.relu = nn.ReLU()
        self.drop = nn.Dropout(dropout)
        self.fc2 = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        x = x.unsqueeze(-1)
        out, (hn, _) = self.lstm(x)
        if self.lstm.bidirectional:
            h = torch.cat((hn[-2], hn[-1]), dim=1)
        else:
            h = hn[-1]
        x = self.relu(self.fc1(h))
        x = self.drop(x)
        return self.fc2(x)

class FingerprintDataset(Dataset):
    def __init__(self, traces, labels, max_length):
        self.traces, self.labels, self.max_length = traces, labels, max_length
    def __len__(self): return len(self.traces)
    def __getitem__(self, idx):
        t = self.traces[idx]
        if len(t)>self.max_length: t=t[:self.max_length]
        else: t=t+[0]*(self.max_length-len(t))
        return torch.FloatTensor(t), torch.LongTensor([self.labels[idx]])[0]


def load_dataset(path):
    with open(path) as f: data=json.load(f)
    if not data: raise ValueError("Empty dataset")
    sites=list({x['website'] for x in data})
    w2l={w:i for i,w in enumerate(sites)}
    l2w={i:w for w,i in w2l.items()}
    traces, labels = [], []
    for it in data:
        td=it['trace_data']
        if isinstance(td,dict) and 'trace_data' in td: td=td['trace_data']
        if isinstance(td,list) and td:
            traces.append(td); labels.append(w2l[it['website']])
    print(f"Loaded {len(traces)} traces for {len(sites)} sites")
    for w in sites: print(f" {w}: {labels.count(w2l[w])}")
    return traces, labels, l2w


def train(model, train_loader, test_loader, crit, opt, epochs, save_path):
    dev=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(dev)
    best_acc=0.0
    for e in range(epochs):
        model.train(); run_loss=0; corr=0; tot=0
        for x,y in train_loader:
            x,y=x.to(dev),y.to(dev)
            opt.zero_grad(); out=model(x); loss=crit(out,y)
            loss.backward(); opt.step()
            run_loss+=loss.item()*x.size(0)
            pred=out.argmax(1); corr+=(pred==y).sum().item(); tot+=y.size(0)
        tr_loss, tr_acc=run_loss/len(train_loader.dataset), corr/tot
        model.eval(); run_loss=0; corr=0; tot=0
        with torch.no_grad():
            for x,y in test_loader:
                x,y=x.to(dev),y.to(dev)
                out=model(x); loss=crit(out,y)
                run_loss+=loss.item()*x.size(0)
                corr+=(out.argmax(1)==y).sum().item(); tot+=y.size(0)
        te_loss, te_acc=run_loss/len(test_loader.dataset), corr/tot
        print(f"Epoch {e+1}/{epochs}, TrLoss={tr_loss:.4f}, TrAcc={tr_acc:.4f}, \
              TeLoss={te_loss:.4f}, TeAcc={te_acc:.4f}")
        if te_acc>best_acc:
            best_acc=te_acc; torch.save(model.state_dict(), save_path)
    return best_acc


def evaluate(model, loader, names):
    dev=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(dev).eval()
    all_p,all_t=[],[]
    with torch.no_grad():
        for x,y in loader:
            x,y=x.to(dev),y.to(dev)
            p=model(x).argmax(1)
            all_p+=p.cpu().tolist(); all_t+=y.cpu().tolist()
    print(classification_report(all_t, all_p, target_names=[names[i] for i in range(len(names))], zero_division=1))
    return all_p,all_t


def main():
    if not os.path.exists(DATASET_PATH):
        print(f"Dataset not found: {DATASET_PATH}"); return
    traces, labels, idx2site = load_dataset(DATASET_PATH)
    if not traces: return
    IN_SIZE = max(len(t) for t in traces)
    ds = FingerprintDataset(traces, labels, IN_SIZE)
    sss=StratifiedShuffleSplit(1, train_size=TRAIN_SPLIT, random_state=42)
    tr_idx, te_idx = next(sss.split(traces, labels))
    tr_ld = DataLoader(Subset(ds,tr_idx), batch_size=BATCH_SIZE, shuffle=True)
    te_ld = DataLoader(Subset(ds,te_idx), batch_size=BATCH_SIZE)
    nc = len(idx2site)
    site_names = [idx2site[i] for i in range(nc)]
    print(f"Classes={nc}, Input={IN_SIZE}, H={HIDDEN_SIZE}, B={BATCH_SIZE}, E={EPOCHS}")
    models = [
        # {'name':'Basic CNN','model':FingerprintClassifier(IN_SIZE,HIDDEN_SIZE,nc),'path':os.path.join(MODELS_DIR,'basic_model.pth')},
        # {'name':'Complex CNN','model':ComplexFingerprintClassifier(IN_SIZE,HIDDEN_SIZE,nc),'path':os.path.join(MODELS_DIR,'complex_model.pth')},
        {'name':'ResNet1D','model':ResNet1DClassifier(IN_SIZE,nc),'path':os.path.join(MODELS_DIR,'resnet1d_model.pth')},
        
    ]
    results={}
    for mi in models:
        print("\n"+"="*40+f"\nTraining {mi['name']}\n"+"="*40)
        crit=nn.CrossEntropyLoss(); opt=optim.Adam(mi['model'].parameters(), lr=LEARNING_RATE)
        acc=train(mi['model'], tr_ld, te_ld, crit, opt, EPOCHS, mi['path'])
        mi['model'].load_state_dict(torch.load(mi['path']))
        print(f"\nEvaluating {mi['name']}:")
        evaluate(mi['model'], te_ld, site_names)
        results[mi['name']]=acc
    print("\nFinal Results:")
    for n,a in results.items(): print(f" {n}: {a:.4f}")
    best=max(results, key=results.get)
    print(f"Best Model: {best} ({results[best]:.4f}) saved at {next(m['path'] for m in models if m['name']==best)}")

if __name__ == '__main__':
    main()
