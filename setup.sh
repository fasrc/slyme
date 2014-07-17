SLYME_ROOT="$(readlink -e $(dirname $BASH_SOURCE))"
export PYTHONPATH="$SLYME_ROOT:$PYTHONPATH"
export PATH="$SLYME_ROOT/bin:$PATH"
