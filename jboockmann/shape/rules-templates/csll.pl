entry(This) :- node(This), next(This, Next), p(Next, This), true.
p(This, P1) :- node(This), next(This, Next), p(Next, P1), true.
p(This, P1) :- node(This), next(This, P1), true.