import os
import sys
import binascii
import struct

class UBootVarList:
	def __init__(self, raw_string):
		self.vars = {}
		raw_string = raw_string[4:] # We don't want the CRC (4 first bytes)

		split_string = [x for x in raw_string.split('\x00') if bool(len(x))]
		for raw_var in split_string:
			split_var = raw_var.split('=', 1)
			self.vars[split_var[0]] = split_var[1]

	def setenv(self, var, value):
		self.vars[var] = value

	def getenv(self, var):
		return self.vars[var]

	def to_raw_string(self):
		raw_string = ""

		for var in self.vars:
			raw_string += var + "=" + self.vars[var] + "\x00"

		# Padding to reach default file size
		# Letting 4 bytes for CRC
		raw_string += "\x00" * (16384 - 4 - len(raw_string))
		crc = binascii.crc32(raw_string) & 0xFFFFFFFF
		raw_string = ''.join(struct.pack("I", crc)[0:4]) + raw_string

		return raw_string

class UBootEnvFile:
	def __init__(self, filename):
		self.filename = filename
		self.size = 16384 # Seems to be the default size for U-Boot env file
		self.raw_string = ""

		try:
			f = open(filename, 'r+b')
		except:
			print "Error : Bad filename."
			raise

		self.raw_string = f.read(self.size)
		self.var_list = UBootVarList(self.raw_string)
		f.close()

	def saveenv(self):
		try:
			f = open(self.filename, 'w+b')
		except:
			raise

		f.write(self.var_list.to_raw_string())
		f.close()

	def setenv(self, var, value):
		self.var_list.setenv(var, value)

	def getenv(self, var):
		return self.var_list.getenv(var)
