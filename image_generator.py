import os

import torch
from torch import autocast
from diffusers import StableDiffusionPipeline

SDV5_MODEL_PATH = 'PATH TO THE MODEL'
save_path = 'SAVE PATH'

def generate_image(prompt, count, save_path):

    if not os.path.exists(save_path):
        os.mkdir(f'{save_path}')

    prompt = prompt
    no = count

    print(f'Character in prompt: {len(prompt)}, limit = 200')

    pipe = StableDiffusionPipeline.from_pretrained(SDV5_MODEL_PATH, revision="fp16", torch_dtype=torch.float16)
    pipe = pipe.to('cuda')

    for i in range(no):
        with autocast('cuda'):
            image = pipe(prompt, guidance_scale=8.5).images[0]

        image_path = os.path.join(save_path, f'{i+1}.png')
        image.save(image_path)
        print(image_path)

    torch.cuda.empty_cache()


if __name__ == '__main__':
    generate_image('cricket bat', 1, save_path)
