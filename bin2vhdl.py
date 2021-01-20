#!/usr/bin/python

from datetime import datetime


VERSION = '2.3.0'

if __name__ == '__main__':
    import getopt
    import os
    import sys

    usage = '''Bin2Vhdl converter utility.
Usage:
    python bin2vhdl.py [options] INFILE [OUTFILE] 

Arguments:
    INFILE          name of bin file for processing.
                    Use '-' for reading from stdin.

    OUTFILE         name of output file. If omitted then output
                    will be writing to stdout.

Options:
    -h, --help              this help message.
    -v, --version           version info.
    --romsize=N             force romsize to N value if greater than output (default: auto).
'''

    # TOKEN TO REPLACE:
    #   {ENTITY_NAME}       ex.: ROM
    #   {ROM_WIDTH_LIMIT}   ex.: 7
    #   {ROM_SIZE_LIMIT}    ex.: 4095
    #   {ROM_SIZE_MASK}     ex.: 11
    
    template_top = '''
-- generated on: {DATE_TIME}

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity {ENTITY_NAME} is
   port(
      clk           : in  std_logic;
      a             : in  std_logic_vector({ROM_SIZE_MASK} downto 0);
      d             : out std_logic_vector({ROM_WIDTH_LIMIT} downto 0)
   );
end {ENTITY_NAME};

architecture arch of {ENTITY_NAME} is

   type byte_rom_type is array (0 to {ROM_SIZE_LIMIT}) of std_logic_vector({ROM_WIDTH_LIMIT} downto 0);
   signal address_latch : std_logic_vector({ROM_SIZE_MASK} downto 0) := (others => '0');

   -- actually memory cells
   signal byte_rom : byte_rom_type := (
   -- ROM contents follows

'''

    template_bottom = '''
   
     );
begin

  ram_process: process(clk, byte_rom)
  begin
      if rising_edge(clk) then
          -- latch the address, in order to infer a synchronous memory
          address_latch <= a;
      end if;
  end process;

  d <= byte_rom(to_integer(unsigned(address_latch)));

end arch;
   
'''


    offset = 0
    forceRomSize = 0

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hv",
                                  ["help", "version", "romsize="])

        for o, a in opts:
            if o in ("-h", "--help"):
                print(usage)
                sys.exit(0)
            elif o in ("-v", "--version"):
                print(VERSION)
                sys.exit(0)
#           elif o in ("--offset"):
#                base = 10
#                if a[:2].lower() == '0x':
#                    base = 16
#                try:
#                    offset = int(a, base)
#                except:
#                    raise getopt.GetoptError('Bad offset value')
                    
            elif o in ("--romsize"):
                base = 10
                if a[:2].lower() == '0x':
                    base = 16
                try:
                    forceRomSize = int(a, base)
                except:
                    raise getopt.GetoptError('Bad offset value')

        if not args:
            raise getopt.GetoptError('Input file is not specified')

        if len(args) > 2:
            raise getopt.GetoptError('Too many arguments')

    except getopt.GetoptError:
        msg = sys.exc_info()[1]     # current exception
        txt = 'ERROR: '+str(msg)    # that's required to get not-so-dumb result from 2to3 tool
        print(txt)
        print(usage)
        sys.exit(2)

    def convert(fin, fout, offset):
    

        with open(fin, "rb") as binaryFile :
            with open(fout, "wt") as newFile:
                data = binaryFile.read()
                fileSize = len(data)
                
                romSizeMask = 1
                romSize = 2
                
                while romSize < fileSize:
                        romSize = romSize << 1
                        romSizeMask = romSizeMask + 1
                
                date_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
                print("Date and time:",date_time)	

                print("Source File Size: " + str(fileSize))
                print("ROM File Size: " + str(romSize))
                print("ROM Mask Bits: " + str(romSizeMask))
                
                if forceRomSize > romSize:      # recalc
                
                    romSizeMask = 1
                    romSize = 2
                
                    while romSize < forceRomSize:
                        romSize = romSize << 1
                        romSizeMask = romSizeMask + 1
                
                    print("\n* ROM Forced to size: " + str(romSize))


                emptyValue = 0
                romData = [emptyValue] * romSize

                print("Len: " + str(len(romData)))


                x = range(0, fileSize)

                for i in x:
                    romData[i] = data[i]


                #return

                
    # TOKEN TO REPLACE:
    #   {ENTITY_NAME}       ex.: ROM
    #   {ROM_WIDTH_LIMIT}   ex.: 7
    #   {ROM_SIZE_LIMIT}    ex.: 4095
    #   {ROM_SIZE_MASK}     ex.: 11
                
                entityName = "ROM"
                romWidth = 8-1
                romSize = romSize - 1
                romSizeMask = romSizeMask - 1
                
                top = template_top.replace("{ENTITY_NAME}", entityName).replace("{ROM_SIZE_LIMIT}", str(romSize)).replace("{ROM_SIZE_MASK}", str(romSizeMask)).replace("{ROM_WIDTH_LIMIT}", str(romWidth)).replace("{DATE_TIME}", date_time)
                
                newFile.write(top)


                chunkSize = 16

                while offset < romSize:

                    strData = "\t" + ', '.join('x\"{:02X}\"'.format(a) for a in romData[offset:offset + chunkSize])
                    
                    if offset < romSize - chunkSize:
                        strData = strData + ", \n"
                    
                    newFile.write(strData)
                    
                    offset = offset + chunkSize
 
                
                newFile.write(template_bottom)


    fin = args[0]
    
    if not os.path.isfile(fin):
        txt = "ERROR: File not found: %s" % fin   # that's required to get not-so-dumb result from 2to3 tool
        print(txt)
        sys.exit(1)

    if len(args) == 2:
        fout = args[1]
    else:
        # write to stdout
        fout = sys.stdout   # compat.get_binary_stdout()

    sys.exit(convert(fin, fout, offset))
	