entry(This) :- node(This), next(This, Next), head(This, This), p(Next, This), true.
p(This, P1) :- node(This), next(This, Next), head(This, P1), p(Next, P1), true.
p(This, P1) :- node(This), next(This, null), head(This, P1), true.
