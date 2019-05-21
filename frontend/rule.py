import itertools

class Rule:
    def __init__(self, cards, before_point):
        self.cards = cards
        self.card_counter = {
            3 : [],
            4 : [],
            5 : [],
            6 : [],
            7 : [],
            8 : [],
            9 : [],
            10 : [],
            11 : [],
            12 : [],
            13 : [],
            14 : [],
            15 : [],
        }
        self.card_type_counter = {
            'clover' : [],
            'diamond' : [],
            'heart' : [],
            'spade' : [],
        }
        self.card_type_sequence = ['diamond', 'clover', 'heart', 'spade']
        self.counting_card()

        self.combo = {
            "pair" : [],
            "trice" : [],
            "straight" : [],
            "flush" : [],
            "four-of-a-kind" : [],
            "full-house" : [],
        }

        self.combo_point = {
            "pair" : [],
            "trice" : [],
            "straight" : [],
            "flush" : [],
            "four-of-a-kind" : [],
            "full-house" : [],
        }

        self.combo_value = {
            'single' : 0,
            'pair' : 1,
            'trice' : 2,
            'straight' : 3,
            'flush' : 4,
            'full-house' : 5,
            'four-of-a-kind' : 6,
            'straight-flush' : 7,
            'royal-flush' : 8,
        }

        self.point_before = before_point
        self.card_combo = -1
        temp = before_point // 1000
        if temp == 0:
            self.card_combo = 1
        elif temp == 1:
            self.card_combo = 2
        elif temp == 2:
            self.card_combo = 3
        elif temp >= 3 and temp <= 8:
            self.card_combo = 5

        if before_point == 0 :
            self.card_combo = -1

        self.generate_combo()

    def counting_card(self):
        index = 0
        for card in self.cards:
            self.card_counter[card.number].append(index)
            self.card_type_counter[card.type].append(index)
            index += 1

    def calculate_point(self, types, number, combo):
        POINT = self.combo_value[combo] * 1000 + number * 10 + types
        return POINT

    def generate_combo(self):
        index_pair = []
        index_trice = []
        index_straight = []
        index_flush = []
        index_four = []
        index_full_house = []

        point_pair = []
        point_trice = []
        point_straight = []
        point_flush = []
        point_four = []
        point_full_house = []
        
        for key, value in self.card_counter.items():
            if len(value) == 2 and (self.card_combo == 2 or self.card_combo == -1):
                largest_type = max(self.card_type_sequence.index(self.cards[value[0]].type), self.card_type_sequence.index(self.cards[value[1]].type))
                point = self.calculate_point(largest_type, self.cards[value[0]].number, 'pair')
                if point > self.point_before :
                    index_pair.append([value[0], value[1]])
                    point_pair.append(point)

            if len(value) == 3 and (self.card_combo == 3 or self.card_combo == -1):
                largest_type = max(self.card_type_sequence.index(self.cards[value[0]].type), self.card_type_sequence.index(self.cards[value[1]].type), self.card_type_sequence.index(self.cards[value[2]].type))
                point = self.calculate_point(largest_type, self.cards[value[0]].number, 'trice')
                if point > self.point_before :
                    index_trice.append([value[0], value[1], value[2]])
                    point_trice.append(point)
            if len(value) == 3 and (self.card_combo == 2 or self.card_combo == -1):
                trice = [value[0], value[1], value[2]]
                for i in [[0,1], [0,2], [1,2]]:
                    largest_type = max(self.card_type_sequence.index(self.cards[trice[i[0]]].type), self.card_type_sequence.index(self.cards[trice[i[1]]].type))
                    point = self.calculate_point(largest_type, self.cards[trice[i[0]]].number, 'pair')
                    if point > self.point_before:
                        point_pair.append(point)
                        index_pair.append([trice[i[0]], trice[i[1]]])

            if len(value) == 4  and (self.card_combo == 5 or self.card_combo == -1):
                for index in range(3,16):
                    if index != key and len(self.card_counter[index]) != 4:
                        for index_card in self.card_counter[index]:
                            point = self.calculate_point(3, self.cards[value[0]].number, 'four-of-a-kind')
                            if point > self.point_before :
                                index_four.append([value[0], value[1], value[2], value[3], index_card])
                                point_four.append(point)
            if len(value) == 4 and (self.card_combo == 2 or self.card_combo == -1):
                four = [value[0], value[1], value[2], value[3]]
                for i in [[0,1], [0,2], [0,3], [1,2], [1,3], [2,3]]:
                    largest_type = max(self.card_type_sequence.index(self.cards[four[i[0]]].type), self.card_type_sequence.index(self.cards[four[i[1]]].type))
                    point = self.calculate_point(largest_type, self.cards[four[i[0]]].number, 'pair')
                    if point > self.point_before:
                        point_pair.append(point)
                        index_pair.append([four[i[0]], four[i[1]]])


            if key <= 11 and (self.card_combo == 5 or self.card_combo == -1):
                straight_exist = True
                for straight_key in range(key, key+5):
                    if len(self.card_counter[straight_key]) == 0 :
                        straight_exist = False
                
                if straight_exist :
                    for straight1 in self.card_counter[key]:
                        for straight2 in self.card_counter[key+1]:
                            for straight3 in self.card_counter[key+2]:
                                for straight4 in self.card_counter[key+3]:
                                    for straight5 in self.card_counter[key+4]:
                                        if self.cards[straight5].type == self.cards[straight4].type and \
                                            self.cards[straight4].type == self.cards[straight3].type and \
                                            self.cards[straight3].type == self.cards[straight2].type and \
                                            self.cards[straight2].type == self.cards[straight1].type :
                                            if self.cards[straight1].number == 11 :
                                                point = self.calculate_point(self.card_type_sequence.index(self.cards[straight5].type), self.cards[straight5].number, 'royal-flush')
                                                if point > self.point_before:
                                                    point_straight.append(point)
                                                    index_straight.append([straight1, straight2, straight3, straight4, straight5])
                                            else :    
                                                point = self.calculate_point(self.card_type_sequence.index(self.cards[straight5].type), self.cards[straight5].number, 'straight-flush')
                                                if point > self.point_before:
                                                    point_straight.append(point)
                                                    index_straight.append([straight1, straight2, straight3, straight4, straight5])
                                        else :
                                            point = self.calculate_point(self.card_type_sequence.index(self.cards[straight5].type), self.cards[straight5].number, 'straight')
                                            if point > self.point_before:
                                                point_straight.append(point)
                                                index_straight.append([straight1, straight2, straight3, straight4, straight5])
        
        for key, value in self.card_type_counter.items():
            if len(value) >= 5 and (self.card_combo == 5 or self.card_combo == -1):
                for permutation in itertools.combinations(value, 5):
                    # permutation = permutation.sort()
                    
                    if self.cards[permutation[0]].number == self.cards[permutation[1]].number-1 and \
                        self.cards[permutation[1]].number == self.cards[permutation[2]].number-1 and \
                        self.cards[permutation[2]].number == self.cards[permutation[3]].number-1 and \
                        self.cards[permutation[3]].number == self.cards[permutation[4]].number-1 :
                        if self.cards[permutation[0]].number == 11 :
                            point = self.calculate_point(self.card_type_sequence.index(self.cards[permutation[-1]].type), self.cards[permutation[-1]].number, 'royal-flush')
                            if point > self.point_before:
                                point_flush.append(point)
                                index_flush.append(permutation)
                        else :
                            point = self.calculate_point(self.card_type_sequence.index(self.cards[permutation[-1]].type), self.cards[permutation[-1]].number, 'straight-flush')
                            if point > self.point_before:
                                point_flush.append(point)
                                index_flush.append(permutation)
                    else :
                        point = self.calculate_point(self.card_type_sequence.index(self.cards[permutation[-1]].type), self.cards[permutation[-1]].number, 'flush')
                        if point > self.point_before:
                            point_flush.append(point)
                            index_flush.append(permutation)

        for pair in index_pair:
            for trice in index_trice:
                if (self.card_combo == 5 or self.card_combo == -1):
                    largest_type = max(self.card_type_sequence.index(self.cards[trice[0]].type), self.card_type_sequence.index(self.cards[trice[1]].type), self.card_type_sequence.index(self.cards[trice[2]].type))
                    point = self.calculate_point(largest_type, self.cards[trice[0]].number, 'full-house')
                    if point > self.point_before:
                        index_full_house.append([pair[0], pair[1], trice[0], trice[1], trice[2]])
                        point_full_house.append(point)

        self.combo['pair'] = index_pair
        self.combo['trice'] = index_trice
        self.combo['straight'] = index_straight
        self.combo['flush'] = index_flush
        self.combo['four-of-a-kind'] = index_four
        self.combo['full-house'] = index_full_house

        self.combo_point['pair'] = point_pair
        self.combo_point['trice'] = point_trice
        self.combo_point['straight'] = point_straight
        self.combo_point['flush'] = point_flush
        self.combo_point['four-of-a-kind'] = point_four
        self.combo_point['full-house'] = point_full_house
            