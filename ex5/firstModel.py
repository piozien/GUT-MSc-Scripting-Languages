import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

url = "https://archive.ics.uci.edu/ml/machine-learning-databases/glass/glass.data"
columns = ['Id', 'RI', 'Na', 'Mg', 'Al', 'Si', 'K', 'Ca', 'Ba', 'Fe', 'Type']
df = pd.read_csv(url, names=columns)

df = df.drop('Id', axis=1)


class_mapping = {1: 0, 2: 1, 3: 2, 5: 3, 6: 4, 7: 5}
df['Type'] = df['Type'].map(class_mapping)

X = df.drop('Type', axis=1).values
y = df['Type'].values

# zbiór treningowy (70%), walidacyjny (15%) i testowy (15%)
X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.15, random_state=42, stratify=y)
X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.176, random_state=42, stratify=y_temp)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)
X_test = scaler.transform(X_test)

X_train_t = torch.tensor(X_train, dtype=torch.float32)
y_train_t = torch.tensor(y_train, dtype=torch.long)
X_val_t = torch.tensor(X_val, dtype=torch.float32)
y_val_t = torch.tensor(y_val, dtype=torch.long)
X_test_t = torch.tensor(X_test, dtype=torch.float32)
y_test_t = torch.tensor(y_test, dtype=torch.long)



class GlassNet(nn.Module):
    def __init__(self):
        super(GlassNet, self).__init__()
        # Warstwa ukryta 1: 9 wejść -> 16 neuronów
        self.fc1 = nn.Linear(9, 16)
        # Funkcja aktywacji ReLU
        self.relu = nn.ReLU()
        # Warstwa wyjściowa: 16 neuronów -> 6 wyjść
        self.fc2 = nn.Linear(16, 6)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        # CrossEntropyLoss z automatycznym SoftMax.
        return x


model = GlassNet()

epochs = 300
learning_rate = 0.01
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

for epoch in range(epochs):
    model.train()

    # Forward pass
    outputs = model(X_train_t)
    loss = criterion(outputs, y_train_t)

    # Backward pass
    optimizer.zero_grad()
    loss.backward()  # gradienty
    optimizer.step()  # aktualizacja wag

    # ocena co 50
    if (epoch + 1) % 50 == 0:
        model.eval()
        with torch.no_grad():
            val_outputs = model(X_val_t)
            val_loss = criterion(val_outputs, y_val_t)
            _, predicted = torch.max(val_outputs, 1)
            correct = (predicted == y_val_t).sum().item()
            accuracy = correct / len(y_val_t) * 100
            print(
                f'Epoka [{epoch + 1}/{epochs}], Loss: {loss.item():.4f}, Val Loss: {val_loss.item():.4f},'
                f' Val Acc: {accuracy:.2f}%')

model.eval()
with torch.no_grad():
    train_out = model(X_train_t)
    _, train_pred = torch.max(train_out, 1)
    train_acc = (train_pred == y_train_t).sum().item() / len(y_train_t) * 100

    val_out_final = model(X_val_t)
    _, val_pred_final = torch.max(val_out_final, 1)
    val_acc_final = (val_pred_final == y_val_t).sum().item() / len(y_val_t) * 100

    test_out = model(X_test_t)
    _, test_pred = torch.max(test_out, 1)
    test_acc = (test_pred == y_test_t).sum().item() / len(y_test_t) * 100

print(f"Skuteczność na danych treningowych: {train_acc:.2f}%")
print(f"Skuteczność na danych walidacyjnych: {val_acc_final:.2f}%")
print(f"Skuteczność na danych testowych: {test_acc:.2f}%")