import numpy as np

class Function_Dict_Class:
    digits =    [x for x in range(48,  58)]
    uppercase = [x for x in range(65,  91)]
    lowercase = [x for x in range(97, 123)]
    from_key = "from"
    to_key   = "to"
    dist_key = "distance"

    class Similarity_Class:
        neg_med = 1.2
        neg_low = 1.1
        vv_low =  0.99
        v_low =   0.9
        low =     0.8
        med =     0.6
        high =    0.4
        v_high =  0.2
        vv_high = 0.1
    
    def __init__(self):
        self.similarity = self.Similarity_Class()

function_dict = Function_Dict_Class()

# -------------------------------- Insertions -------------------------------- #
insert_costs = np.ones(128)

#Lower weight
insert_costs[ord('-')] = function_dict.similarity.vv_high
insert_costs[ord(' ')] = function_dict.similarity.vv_high

# --------------------------------- Deletions -------------------------------- #
delete_costs = np.ones(128)
delete_costs[ord('-')] = function_dict.similarity.vv_high
delete_costs[ord(' ')] = function_dict.similarity.vv_high

# ------------------------------- Substitutions ------------------------------ #
substitute_costs = np.ones((128, 128))

#Common errors will have arbitrary weights applied as I see fit.
errors_list = [
    ["O", "0", function_dict.similarity.v_high],
    ["o", "0", function_dict.similarity.v_high],
    ["B", "8", function_dict.similarity.v_high],
    ["m", "n", function_dict.similarity.high  ],
    ["u", "v", function_dict.similarity.high  ],
    ["Z", "2", function_dict.similarity.high  ],
    ["G", "6", function_dict.similarity.high  ],
    ["I", "1", function_dict.similarity.high  ],
    ["c", "e", function_dict.similarity.med   ],
    ["D", "O", function_dict.similarity.med   ],
    ["C", "G", function_dict.similarity.med   ],
    ["M", "N", function_dict.similarity.med   ],
    ["U", "V", function_dict.similarity.med   ],
    ["1", "7", function_dict.similarity.med   ],
    ["b", "6", function_dict.similarity.med   ],
    ["E", "F", function_dict.similarity.med   ],
    ["D", "0", function_dict.similarity.med   ],
    ["S", "5", function_dict.similarity.med   ],
    ["T", "7", function_dict.similarity.med   ],
    ["T", "I", function_dict.similarity.low   ],
    ["g", "q", function_dict.similarity.low   ],
    ["L", "I", function_dict.similarity.low   ],
    ["S", "9", function_dict.similarity.low   ],
]

#Iterate through the list and add it to the list of substitutions, along with the transpose equivalent
for key_1, key_2, weight in errors_list:
    substitute_costs[ord(key_1), ord(key_2)] = weight
    substitute_costs[ord(key_2), ord(key_1)] = weight


# ------------------------------ Transpositions ------------------------------ #
transpose_costs = np.ones((128,128))