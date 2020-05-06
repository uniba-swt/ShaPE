entry(This) :- node(This), next(This, Next), p(Next), true.
p(This) :- node(This), next(This, Next), p(Next), true.
p(This) :- node(This), next(This, This), true.