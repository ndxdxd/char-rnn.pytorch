

import torch
import os
import argparse

from helpers import *
from model import *

def generate(decoder, prime_str='A', predict_len=1000, temperature=0.8, cuda=False):
    with torch.no_grad():  # Disable gradient computation
        hidden = decoder.init_hidden(1)
        prime_input = Variable(char_tensor(prime_str).unsqueeze(0))

        if cuda:
            if isinstance(hidden, tuple):  # Check if LSTM
                hidden = (hidden[0].cuda(), hidden[1].cuda())  # Move both tensors
            else:
                hidden = hidden.cuda()
            prime_input = prime_input.cuda()
        
        predicted = prime_str

        for p in range(len(prime_str) - 1):
            _, hidden = decoder(prime_input[:, p], hidden)

        inp = prime_input[:, -1]

        for p in range(predict_len):
            output, hidden = decoder(inp, hidden)

            output_dist = output.data.view(-1).div(temperature).exp()
            top_i = torch.multinomial(output_dist, 1)[0]
            predicted_char = all_characters[top_i]

            predicted += predicted_char
            inp = Variable(char_tensor(predicted_char).unsqueeze(0))

            if cuda:
                inp = inp.cuda()

    return predicted

# Run as standalone script
if __name__ == '__main__':

# Parse command line arguments
    argparser = argparse.ArgumentParser()
    argparser.add_argument('filename', type=str)
    argparser.add_argument('-p', '--prime_str', type=str, default='A')
    argparser.add_argument('-l', '--predict_len', type=int, default=100)
    argparser.add_argument('-t', '--temperature', type=float, default=0.8)
    argparser.add_argument('--cuda', action='store_true')
    args = argparser.parse_args()

    decoder = torch.load(args.filename)
    del args.filename
    print(generate(decoder, **vars(args)))

