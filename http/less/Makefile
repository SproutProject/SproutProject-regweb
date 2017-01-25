LESS=lessc
CSS=mask.css index.css plan.css about.css qa.css poll.css indiv.css

all: $(CSS)

%.css: %.less
	$(LESS) $< > ../stylesheets/css/$@
