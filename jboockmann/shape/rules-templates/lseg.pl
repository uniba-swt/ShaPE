entry(P0, This)  :-  node(This), next(This, null), true, p(P0, This), true.
p(This, P1)  :-  node(This), next(This, P1), true, true.
p(This, P1)  :-  node(This), next(This, Next), p(Next, P1), true.