# bin2vhdl
Simple Python script to convert a BIN file to a VHDL Entity ROM

Bin2Vhdl converter utility.
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
