from django.shortcuts import render
# Import standard dependencies
import cv2
import os
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader
from torchsummary import summary
import torchinfo
import glob
import uuid
from PIL import Image
import torch.nn.functional as F
from rest_framework.views import APIView

from utils.response import success_response, fail_response

# Define the FaceRecognitionView class that inherits from APIView
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class EmbeddingModel(nn.Module):
    def __init__(self, embedding_size=128):
        super(EmbeddingModel, self).__init__()
        self.conv1 = nn.Conv2d(3, 64, kernel_size=10, padding=1)
        self.maxpool1 = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(64, 128, kernel_size=7, padding=1)
        self.maxpool2 = nn.MaxPool2d(2, 2)
        self.conv3 = nn.Conv2d(128, 128, kernel_size=4, padding=1)
        self.maxpool3 = nn.MaxPool2d(2, 2)
        self.conv4 = nn.Conv2d(128, 256, kernel_size=4, padding=1)
        self.flatten = nn.Flatten()
        self.dense = nn.Linear(256 * 9 * 9, embedding_size)
        self.normalize = nn.functional.normalize

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = self.maxpool1(x)
        x = torch.relu(self.conv2(x))
        x = self.maxpool2(x)
        x = torch.relu(self.conv3(x))
        x = self.maxpool3(x)
        x = torch.relu(self.conv4(x))
        x = self.flatten(x)
        x = self.dense(x)
        x = self.normalize(x, p=2, dim=1)
        return x

class SiameseModel(nn.Module):
    def __init__(self, embedding_size=128):
        super(SiameseModel, self).__init__()
        self.embedding = EmbeddingModel(embedding_size=embedding_size)
        self.device = torch.device("cuda" if torch.cuda.is_available() else 'cpu')
        self.to(self.device)

    def forward(self, x):
        return self.embedding(x)

# Define transform for inference
inference_transform = transforms.Compose([
    transforms.Resize((100, 100)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])


def get_embedding(img_path, model, transform):
    img = Image.open(img_path).convert("RGB")
    img = transform(img).unsqueeze(0).to(device)  
    with torch.no_grad():
        embedding = model.embedding(img)
        embedding = embedding[0]
    return embedding


class FaceRecognitionView(APIView):

    def __init__(self, **kwargs):
        # Initialize the model globally
        checkpoint = torch.load(os.path.join('./0.0254_checkpoint.pth'), map_location=torch.device('cpu'))
        model = SiameseModel(embedding_size=128).to(device)
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()
        self.model = model

    def post(self, request):
        # Get iamge file from request
        image_file = request.FILES.get('image')
        if not image_file:
            return fail_response("No image file provided")
        
        #Generate embedding for the input image
        embeding = get_embedding(image_file, self.model, inference_transform)
        if embeding is None:
            return fail_response("Failed to generate embedding for the image")
        print(embeding.shape)
        return success_response({
            "embedding": embeding.cpu().numpy().tolist()  # Convert tensor to list for JSON serialization
        })