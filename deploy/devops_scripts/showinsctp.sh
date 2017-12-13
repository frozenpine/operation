echo ctp
[[ -s CtpInstrumentfile.ini ]] && {
	echo "Total instruments count: `cat CtpInstrumentfile.ini | wc -l`"
} || {
	echo "No instruments exists." >&2
	exit 1
}
