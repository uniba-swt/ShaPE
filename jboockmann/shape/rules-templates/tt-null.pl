% a ternarry tree
% TODO: some entry and p rules are still missing here
entry(This)  :-  node(This), left(This, Left), mid(This, Mid), right(This, Right), p(Right), p(Mid), p(Left), true.
p(This)  :-  node(This), left(This, null), mid(This, null), right(This, null), true, true.