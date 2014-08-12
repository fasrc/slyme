# Copyright (c) 2013-2014
# Harvard FAS Research Computing
# All rights reserved.

"""unit tests

This requires a clone of https://github.com/fasrc/slurm_utils, for its example_jobs.
"""

import sys, os
import unittest, mock

import slyme
from slyme import util, jobs

import settings


class SankeyTestCase(unittest.TestCase):
	def test_sacct_bulk(self):
		with mock.patch('slyme.jobs._yield_raw_sacct_job_lines') as m:
			m.return_value = open(os.path.join(os.path.dirname(__file__), '_mock_data', 'sacct_bulk_parsable.out'))

			users = {}
			nodes = {}
			states = {}

			users_nodes = {}
			nodes_states = {}
	
			for j in jobs.get_jobs(filter=lambda j: j['State'] in ('COMPLETED','FAILED')):
				if j['NCPUS']==1 and not j['NodeList_str'].startswith('None'):
					#if j['User'].startswith('g'):
					if j['NodeList_str']=='aag06':
					#if j['Partition']=='serial_requeue':
					#if True:
						#EAFP b/c assuming presence much more common

						#sankey nodes
						users[j['User']] = None
						nodes[j['NodeList_str']] = None
						states[j['State']] = None

						#sankey links
						try:
							users_nodes[(j['User'],j['NodeList_str'])] += 1
						except KeyError:
							users_nodes[(j['User'],j['NodeList_str'])] = 1
						try:
							nodes_states[(j['NodeList_str'],j['State'])] += 1
						except KeyError:
							nodes_states[(j['NodeList_str'],j['State'])] = 1
						
						#print j['User'], j['NodeList_str'], j['State']

			sankey_nodes = []  #string: name
			sankey_links = []  #tuple: (source_index, target_index, value)

			#sankey node number
			i = 0
			for k in users.keys():
				users[k] = i
				sankey_nodes.append(k)
				i += 1
			for k in nodes.keys():
				nodes[k] = i
				sankey_nodes.append(k)
				i += 1
			for k in states.keys():
				states[k] = i
				sankey_nodes.append(k)
				i += 1

			for User in users.keys():
				for Node in nodes.keys():
					try:
						sankey_links.append((users[User], nodes[Node], users_nodes[(User, Node)]))
					except KeyError:
						pass
			for Node in nodes.keys():
				for State in states.keys():
					try:
						sankey_links.append((nodes[Node], states[State], nodes_states[(Node, State)]))
					except KeyError:
						pass

			with open('user_node_state.json','w') as f:
				#bummer that json doesn't like trailing commas on last entry; otherwise this would look cleaner
				
				f.write('{\n')
				f.write('"nodes":[\n')
				for i, node in enumerate(sankey_nodes):
					f.write('{"name":"%s"}' % node)
					if i!=(len(sankey_nodes)-1):
						f.write(',')
					f.write('\n')
				f.write(']\n')
				
				f.write(',\n')

				f.write('"links":[\n')
				for i, link in enumerate(sankey_links):
					f.write('{"source":%d,"target":%d,"value":%d}' % (link[0], link[1], link[2]))
					if i!=(len(sankey_links)-1):
						f.write(',')
					f.write('\n')
				f.write(']\n')
				f.write('}\n')


if __name__=='__main__':
	unittest.main()
