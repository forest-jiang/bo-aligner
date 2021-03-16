# bo-aligner

For the effort of improving sentence aligner for collecting Tibetan parallel sentences.
This is a public repo where licensed content has been removed.

The output bisentences are summarized in `bisent_log.csv`

TODOs:
* Experiment: currently Hunalign favors 1-to-1 alignment, but that is not the case for Tibetan text, where one "sentence" corresponding to one or more pieces separated by "shay". Need to check whether we need to change the code for this.
* Experiment: check the benefit of stemming the tokens before aligning.
* Experiment: void trivialTranslateWord() doesn't consider the numbers in Tibetan script. Let's add that.
