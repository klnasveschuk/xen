#!/usr/bin/python
###########
# Author: Kent L Nasveschuk
# Date: 10-2015
# Version: 1.0
##########

import sys
import subprocess
import paramiko
# VM Name/function, UUID, guest IP, Xen host IP
PRIVKEY = '/home/kln/.ssh/id_rsa'
xen_hosts = { 'xen1':'192.168.1.30','xen2':'192.168.1.31' }
#xen_hosts = { 'xen2':'192.168.1.31' }
WAIT = 5
################################################
def run_cmd(host,cmd):
	
	try:
		#print CMD
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(host,username='root',key_filename=PRIVKEY)
	except paramiko.AuthenticationException:
		print "Authentication failed when connecting to %s" % host
		sys.exit(1)

	try:
		stdin, stdout, stderr = ssh.exec_command(cmd)
		mydict = {}
		attr = []
		name = ''
		ps = ''
		uuid = ''
		if stdout:
			x = stdout.readlines()
			for i in x:
				new = i.split(':')
				if 'uuid' in new[0]:
					uuid = new[1].strip()
				if 'name-label' in new[0]:
					name = new[1].strip()
				if 'power-state' in new[0]:
					ps = new[1].strip()
					#print 'guest:' + new[1]
				if name and ps and uuid:
					#print mydict
					if 'Controldomainonhost' in name:
						pass
					else:
						attr.append(uuid)
						attr.append(ps)
						attr.append(host)
						mydict.update({name:attr})
					ps = ''
					uuid = ''
					name = ''
					attr = []
			return mydict
			#for i in x:
			#	key2,val2 = x[i].split(':')
			#	if 'UUID' in key2:
			#		print val2
		if not stderr:
			print 'Error: ' + str(stderr.readlines())
		else:
			pass
		ssh.close()
	except:
		print 'Unexpected error: ', sys.exc_info()[0]
		raise
################################################
def control_vm(key,attr,CMD_STUB):
	#print key,attr
	#sys.exit()
	SKIP = 1
	#print vms,key,CMD_STUB
	#sys.exit()
	try:
		#print CMD
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(attr[2],username='root',key_filename=PRIVKEY)
	except paramiko.AuthenticationException:
		print "Authentication failed when connecting to %s" % attr[2]
		sys.exit(1)

	try:
		if 'running' in attr[1] and 'start' in CMD_STUB:
			print key + ' is already running'
			SKIP = 0
		elif 'halted' in attr[1]  and 'shutdown' in CMD_STUB:
			print key + ' is already shutdown'
			SKIP = 0

		if SKIP == 1 :
			CMD = CMD_STUB + attr[0]
			print 'Executing ' + CMD + ' for VM ' + key
			try:
				stdin, stdout, stderr = ssh.exec_command(CMD)
				if not stderr:
					print 'Error: ' + str(stderr.readlines())
				else:
					pass
			except:
				print 'Unexpected error: ', sys.exc_info()[0]
				raise
		ssh.close()
	except:
		print 'Unexpected error: ', sys.exc_info()[0]
		raise

################################################
def main(answer):
	try:
		if 'start' in answer:
			for key,value in vms.iteritems():
				msg = 'Start ' + key + ''' (y/n):'''
				yn = raw_input(msg)
				if yn == 'y':
					CMD_STUB = 'xe vm-start vm='
					control_vm(key,value,CMD_STUB)
				else:
					print 'Skip ' + key
		elif 'stop' in answer:
			for key,value in vms.iteritems():
				msg = 'Stop ' + key + ''' (y/n):'''
				yn = raw_input(msg)
				if yn == 'y':
					CMD_STUB = 'xe vm-shutdown vm='
					control_vm(key,value,CMD_STUB)
				else:
					print 'Skip ' + key


		else:
			print '''Usage: "start" or "stop" to control VMs'''
			sys.exit()
	except:
		print 'Unexpected error: ', sys.exc_info()[0]
		raise

# Main
for key,val in xen_hosts.iteritems():
	cmd = 'ping -w 1 -c 1 ' + val + ' 1>/dev/null'
	retval = subprocess.call(cmd,shell=True)
	if retval == 0:
		print key + ' is ready for commands\n'
		cmd = 'xe vm-list |tr -d [:blank:]'
		vms = run_cmd(val,cmd)
		answer = raw_input('start/stop VMs: ')
		main(answer)
	elif retval == 1:
		print '\n' + key + ' is unavailable'

