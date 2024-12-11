import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models

class ImageFeatureExtractor(nn.Module):
    def __init__(self):
        super(ImageFeatureExtractor, self).__init__()
        self.model = models.mobilenet_v2(pretrained=True).features
        for param in self.model.parameters():
            param.requires_grad = False  # Freeze layers

    def forward(self, x):
        return self.model(x)

class TextFeatureExtractor(nn.Module):
    def __init__(self, input_dim=768, output_dim=128):
        super(TextFeatureExtractor, self).__init__()
        self.projection = nn.Linear(input_dim, 300)
        self.fc = nn.Linear(300, output_dim)

    def forward(self, x):
        x = F.relu(self.projection(x))
        return F.relu(self.fc(x))

class JointModel(nn.Module):
    def __init__(self, embedding_dim=300, num_classes=29):
        super(JointModel, self).__init__()
        self.image_model = ImageFeatureExtractor()

        self.title_model = TextFeatureExtractor(input_dim=768, output_dim=128)
        self.description_model = TextFeatureExtractor(input_dim=768, output_dim=128)

        self.fc1 = nn.Linear(1280 + 128 + 128, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, num_classes)

    def forward(self, image, title, description):
        image_features = self.image_model(image)
        image_features = image_features.mean(dim=[2, 3])
    
        title_features = self.title_model(title)
        description_features = self.description_model(description)

        combined = torch.cat([image_features, title_features, description_features], dim=1)

        x = F.relu(self.fc1(combined))
        x = F.relu(self.fc2(x))
        return self.fc3(x)
