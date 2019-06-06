import torch.nn.functional as F
import torch.nn as nn
import torch

"""
Spatial Broadcast Decoder Module
https://arxiv.org/pdf/1901.07017.pdf 
"""
class SBD(torch.nn.Module):
	def __init__(self, z_dim, img_dim, out_channels=3):
		super(SBD, self).__init__()

		self.H, self.W = img_dim
		x_range = torch.linspace(-1.,1.,self.W)
		y_range = torch.linspace(-1.,1.,self.H)
		x_grid, y_grid = torch.meshgrid([x_range,y_range])
		self.register_buffer('x_grid', x_grid.view((1, 1) + x_grid.shape))
		self.register_buffer('y_grid', y_grid.view((1, 1) + y_grid.shape))

		self.conv_layer = torch.nn.Sequential(
			torch.nn.Conv2d(z_dim+2,64,kernel_size=3,stride=1,padding=1),
			torch.nn.ELU(),
			torch.nn.Conv2d(64,64,kernel_size=3,stride=1,padding=1),
			torch.nn.ELU(),
			torch.nn.Conv2d(64,64,kernel_size=3,stride=1,padding=1),
			torch.nn.ELU(),
			torch.nn.Conv2d(64,64,kernel_size=3,stride=1,padding=1),
			torch.nn.ELU(),
			torch.nn.Conv2d(64,out_channels,kernel_size=3,stride=1,padding=1))

		# ## Additional MLP Layer -> according to KG should improve reconstruction quality at cost of disentanglement
		# self.pre_mlp = torch.nn.Sequential(
		# 	torch.nn.Linear(z_dim,z_dim),
		# 	torch.nn.ELU(),
		# 	torch.nn.Linear(z_dim,z_dim),
		# 	torch.nn.ELU())

	def forward(self,z):
		N = z.shape[0]
		# z = self.pre_mlp(z)

		z_broad = z.view(z.shape + (1,1))
		z_broad = z_broad.expand(-1,-1,self.H,self.W)
		vol = torch.cat((self.x_grid.expand(N,-1,-1,-1),
			self.y_grid.expand(N,-1,-1,-1),z_broad), dim=1)
		conv_out = self.conv_layer(vol)
		
		mu_x = torch.sigmoid(conv_out[:,:3,:,:])
		ret = torch.cat((mu_x,conv_out[:,(3,),:,:]),dim=1)
		return ret

