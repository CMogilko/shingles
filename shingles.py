# -*- coding: UTF-8 -*-
from optparse import OptionParser
import random
import itertools


MAXGENPRIMEINDEX = 20
MINGENPRIMTINDEX = 5

HASH_COUNT = 84
SUPERGROUPS = 6
SUPER_SIZE = HASH_COUNT / SUPERGROUPS


def gen_prime(index):
    D = {}
    q = 2
    gen_index = 0
    while True:
        if q not in D:
            gen_index += 1
            if gen_index == index:
            	return q
            D[q * q] = [q]
        else:
            for p in D[q]:
                D.setdefault(p + q, []).append(p)
            del D[q]
        q += 1


def readfile(filename):
	with open(filename) as f:
		return f.read().replace('\n', ' ')


def canonize(source):
	stop_symbols = '.,!?:;-\n\r()'
	stop_words = (u'это', u'как', u'так', u'и', u'в', u'над', u'к', u'до', u'не', u'на', u'но', u'за', u'то', u'с', 
		u'ли', u'а', u'во', u'от', u'со', u'для', u'о', u'же', u'ну', u'вы', u'бы', u'что', u'кто', u'он', u'она')
	return ([x for x in [y.strip(stop_symbols).decode('UTF-8') for y in source.lower().split()] if x and (x not in stop_words)])


def gen_hash():
	prime = gen_prime(random.randint(MINGENPRIMTINDEX, MAXGENPRIMEINDEX))
	base = random.randint(prime, 2*prime)
	return (base, prime)


def prepare_hashes(count):
	return [gen_hash() for i in xrange(count)]


def calc_hash(shingle, func):
	s = ''.join(shingle)
	base, prime = func
	value = 0
	for i in xrange(len(s)):
		value += ord(s[i])*pow(base, i) % prime
	return value


def calc_shingles(text, size, hashes):
	matrix = []
	for i in xrange(len(text) - (size - 1)):
		shignle = [x for x in text[i:i + size]]
		matrix.append([calc_hash(shignle, func) for func in hashes])
	transposed = map(list, zip(*matrix))
	return [min(transposed[i]) for i in xrange(HASH_COUNT)]


def compare_shingles(shingles1, shingles2):
	same = 0.0
	for h1, h2 in zip(shingles1, shingles2):
		if h1 == h2:
			same += 1.0
	return same / HASH_COUNT


def gen_super_map():
    m = [None]*HASH_COUNT
    used = [False]*HASH_COUNT
    for i in xrange(SUPERGROUPS):
        for j in xrange(SUPER_SIZE):
            k = random.randint(0, HASH_COUNT - 1)
            while used[k]:
                k = random.randint(0, HASH_COUNT - 1)
            used[k] = True
            m[k] = (i, j)
    return m


def calc_super(shingles, mapping):
    ret = [[None]*SUPER_SIZE]*SUPERGROUPS
    for i in xrange(HASH_COUNT):
        num, idx = mapping[i]
        ret[num][idx] = shingles[i]
    return ret


def compare_super(sup1, sup2):
	sum = 0.0
	for i in xrange(SUPERGROUPS):
		eq = True
		for j in xrange(SUPER_SIZE):
			if sup1[i][j] != sup2[i][j]:
				eq = False
		if eq:
			sum += 1.0
	return sum / SUPERGROUPS


def calc_mega(supers, combinations):
	megas = []
	for i, j in combinations:
		m = list(supers[i])
		m.extend(supers[j])
		megas.append(m)
	return megas


def compare_mega(megas1, megas2):
	same = 0.0
	for m1, m2 in zip(megas1, megas2):
		eq = True
		for e1, e2 in zip(m1, m2):
			if e1 != e2:
				eq = False
		if eq:
			same += 1.0
	return same / len(megas1)


def main():
    parser = OptionParser()
    parser.add_option("-a", "--file1")
    parser.add_option("-b", "--file2")
    parser.add_option("-s", "--size", type='int', default=10)
    (options, args) = parser.parse_args()

    text1 = canonize(readfile(options.file1))
    text2 = canonize(readfile(options.file2))

    hashes = prepare_hashes(HASH_COUNT)

    shingles1 = calc_shingles(text1, options.size, hashes)
    shingles2 = calc_shingles(text2, options.size, hashes)

    print "shingles compare: ", compare_shingles(shingles1, shingles2)

    m = gen_super_map()
    sup1 = calc_super(shingles1, m)
    sup2 = calc_super(shingles2, m)

    print "super compare: ", compare_super(sup1, sup2)

    comb = list(itertools.combinations(xrange(SUPERGROUPS), 2))
    mega1 = calc_mega(sup1, comb)
    mega2 = calc_mega(sup2, comb)

    print "mega compare: ", compare_mega(mega1, mega2)


if __name__ == '__main__':
	main()
