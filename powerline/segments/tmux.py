# vim:fileencoding=utf-8:noet
from __future__ import (unicode_literals, division, absolute_import, print_function)

from powerline.bindings.tmux import get_tmux_output
from powerline.lib.shell import readlines, which
from powerline.segments import with_docstring
from powerline.lib.threaded import ThreadedSegment


def attached_clients(pl, minimum=1):
	'''Return the number of tmux clients attached to the currently active session

	:param int minimum:
		The minimum number of attached clients that must be present for this 
		segment to be visible.
	'''
	session_output = get_tmux_output(pl, 'list-panes', '-F', '#{session_name}')
	if not session_output:
		return None
	session_name = session_output.rstrip().split('\n')[0]

	attached_clients_output = get_tmux_output(pl, 'list-clients', '-t', session_name)
	attached_count = len(attached_clients_output.rstrip().split('\n'))

	return None if attached_count < minimum else str(attached_count)


class MemCpuLoadSegment(ThreadedSegment):
	memory_opts = {'default' : '0',
				   'free': '1',
				   'percentage': '2'
				   }

	def set_state(self, refresh_interval=1.0, num_cpu_bars=10,
				  memory_mode='default', num_average_load=3, **kwargs):
		self.num_average_load = num_average_load
		self.set_interval(interval=refresh_interval)
		self.num_cpu_bars = num_cpu_bars
		self.memory_mode = memory_mode
		super(MemCpuLoadSegment, self).set_state(**kwargs)

	def update(self, old_stats):
		if which('tmux-mem-cpu-load'):
			mem_mode = MemCpuLoadSegment.memory_opts[self.memory_mode]
			stats = next(readlines(['tmux-mem-cpu-load',
									'-a', '0',
									'-g', str(self.num_cpu_bars),
									'-i', str(self.interval),
									'-a', str(self.num_average_load),
									'-m', mem_mode
									], None))
			return stats
		return None

	def render(self, stats, **kwargs):
		if not stats:
			return None
		return [{'contents': stats,
				 'highlight_groups': ['mem_cpu_load'],	
				 'divider_highlight_group': None}]


mem_cpu_load = with_docstring(MemCpuLoadSegment(),
'''MemCpuSegment interfaces with https://github.com/thewtex/tmux-mem-cpu-load/
for easier integration to powerline.
Basically 3 sources of information are available:

1) cpu usage percentage + corresponding graph bar
2) memory usage customizable with 3 different display modes as explained in
param section below
3) average system load - choice of 0 - 3 averages (passed 1min, 5mins, 15mins)

:param float refresh_interval:
	how often to refresh the widget (value must be greater than 1.0)
:param str memory_mode:
	mode to present memory usage in:
	a) 'default' : prints ratio used/total
	b) 'free' : prints total free memory
	c) 'percentage' : is pretty self explanatory - ratio as percentage
:param int num_cpu_bars:
	number of bars to use in cpu usage bar graph plot
:param int num_average_load:
	number of system load averages to render (value must be in [0, 3])
''')
