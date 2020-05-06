entry(This) :- node(This), next(This, null), true.
entry(This) :- node(This), next(This, Next), p(Next), true.
p(This) :- node(This), next(This, Next), p(Next), true.
p(This) :- node(This), next(This, null), true.