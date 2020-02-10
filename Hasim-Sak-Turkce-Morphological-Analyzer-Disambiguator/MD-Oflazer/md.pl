#!/usr/bin/perl
#Author: Haşim Sak @ Department of Computer Engineering - Boğaziçi University.
#Email: hasim.sak@gmail.com
#Version: 1.0
#Date: August 17, 2007
#Description: This program implements an averaged perceptron based morphological disambiguation system for Turkish text.
#             You can find the most up to date version at http://www.cmpe.boun.edu.tr/~hasim.
#             For more information, you can see readme.txt and read the following paper.
#             Haşim Sak, Tunga Güngör, and Murat Saraçlar. Morphological disambiguation of Turkish text with perceptron algorithm.
#             In CICLing 2007, volume LNCS 4394, pages 107-118, 2007.
#             If you want to use this program in your research, please cite this paper.
#             Please note that this implementation is a little bit different than the one described in the paper.
#             The difference is that the baseline model is no longer used and the disambiguation is done using Viterbi decoding.
#Important: The input files are expected to be UTF-8 encoded. You can use iconv unix command line tool for encoding conversions.

use strict;
use utf8;
use open ":utf8";
$| = 1;


binmode STDIN, ":utf8";
binmode STDOUT, ":utf8";

my $num_examples;
my %w;
my %avgw;
my %counts;

my %exclude_feat;

if (@ARGV != 3 && @ARGV != 4)
{
	print "usage: md.pl -train train_set[in] dev_set[in] model[out]\n";
	print "usage: md.pl -test model[in] test_set[in]\n";
	print "usage: md.pl -disamb model[in] amb_set[in] unamb_set[out]\n";
	print "please use utf-8 encoding for input files\n";
	exit(-1);
}

srand(792349);

if ($ARGV[0] eq "-train")
{
	train($ARGV[1], $ARGV[2], $ARGV[3]);
}
elsif ($ARGV[0] eq "-test")
{
	load_model($ARGV[1]);
	my $accuracy = test($ARGV[2]);
	print "accuracy = ", $accuracy, "\n";
}
elsif ($ARGV[0] eq "-disamb")
{
	load_model($ARGV[1]);
	disamb($ARGV[2], $ARGV[3]);
}

sub train
{
	my ($train_file, $dev_file, $model_file) = @_;
	$num_examples = 0;
	for (my $iter = 1; $iter <= 4; ++$iter)
	{
		one_pass($train_file);
		my $accuracy = test($dev_file);
		print "$iter. iter: $accuracy\n";
	}
	#update averaged perceptron weights and save
	save_model($model_file);
}

sub one_pass
{
	my ($train_file) = @_;
	my $TRAIN;
	open($TRAIN, $train_file) || die("cannot open file: $train_file\n");
	my $line;
	my @words;
	my @correct_parse;
	my @allparses;
	
	while (read_sentence($TRAIN, \@words, \@correct_parse, \@allparses))
	{
		++$num_examples;		
		my ($best_score, @best_parse) = best_parse(0, @allparses);		
		my %feat_correct;
		if ("@correct_parse" eq "@best_parse")
		{
			next;
		}
		extract_features(\%feat_correct, @correct_parse);
		my %feat_best;
		extract_features(\%feat_best, @best_parse);
		update_model(\%feat_correct, \%feat_best);
	}
	close($TRAIN);
	foreach my $feat (keys %avgw)
	{
		$avgw{$feat} = ($avgw{$feat} * $counts{$feat} + ($num_examples - $counts{$feat}) * $w{$feat})/$num_examples;
		$counts{$feat} = $num_examples;
	}
}

sub test
{
	my ($test_file) = @_;
	
	my $TEST;
	open($TEST, $test_file) || die("cannot open file: $test_file\n");
	my $line;
	my @words;
	my @correct_parse;
	my @allparses;
	my $num_correct = 0;
	my $num_token = 0;
	
	while (read_sentence($TEST, \@words, \@correct_parse, \@allparses))
	{
		my ($best_score, @best_parse) = best_parse(1, @allparses);
		
		for (my $i = 0; $i < @correct_parse; ++$i)
		{
			if ($correct_parse[$i] eq $best_parse[$i])
			{
				++$num_correct;
			}
			++$num_token;
		}
	}
	close($TEST);
	if ($num_token > 0)
	{
		return 100*$num_correct/$num_token 		
	}
	return 0;
}

sub disamb
{
	my ($amb_file, $unamb_file) = @_;
	
	my $TEST;
	open($TEST, $amb_file) || die("cannot open file: $amb_file\n");

	my $OUT;
	open($OUT, ">$unamb_file") || die("cannot open file: $unamb_file\n");

	my @words;
	my @allparses;
	
	my $line;
	while ($line = <$TEST>)
	{
		chomp($line);
		if ($line =~ /<DOC>/ || $line =~ /<\/DOC>/ || $line =~ /<TITLE>/ || $line =~ /<\/TITLE>/ || $line =~ /<S>/)
		{
			print "$line\n";
			next;
		}
		if ($line =~ /<\/S>/)
		{
			my ($best_score, @best_parse) = best_parse(1, @allparses);
			for (my $i = 0; $i < @words; ++$i)
			{
				print $OUT "$words[$i] $best_parse[$i]\n";				
			}
			@words = ();
			@allparses = ();
			next;
		}
		my @tokens = split(/\s+/, $line);
		push(@words, shift(@tokens));
		push(@allparses, "@tokens");
	}
	close($TEST);
	close($OUT);
}

sub best_parse
{
	my ($averaged_perceptron, @allparses) = @_;
	push(@allparses, "</s>");
	my %bestpath;
	$bestpath{0} = "-1 0 null";
	my $best_state_num = 0;
	my $best_score;
	my %states;
	$states{"<s> <s>"} = 0;
	my $n = 0;
	foreach my $str (@allparses)
	{
		$best_score = -100000;
		my %next_states;
		my @cands = split(/\s+/, $str);
		#shuffle candidates
		for (my $j = 0; $j < @cands; ++$j)
		{
			my $k = rand(@cands);
			my $temp = $cands[$j];
			$cands[$j] = $cands[$k];
			$cands[$k] = $temp;
		}
		
		foreach my $cand (@cands)
		{
			foreach my $state (keys %states)
			{
				my $state_num = $states{$state};
				my ($prev, $score, $parse) = split(/\s+/, $bestpath{$state_num});

				my @hist = split(/\s+/, $state);
				my @trigram = ($hist[0], $hist[1], $cand);
				my %feat;
				extract_trigram_feat(\%feat, @trigram);
				my $trigram_score;
				if ($averaged_perceptron)
				{
					$trigram_score = ascore(\%feat);
				}
				else
				{
					$trigram_score = score(\%feat);
				}				
				my $new_score = $score + $trigram_score;

				my $new_state = "$hist[1] $cand";
				if (!defined $next_states{$new_state})
				{
					$next_states{$new_state} = ++$n;
				}
				my $next_state_num = $next_states{$new_state};

				if (defined $bestpath{$next_state_num})
				{
					my ($ignore, $cur_score, $ignore) = split(/\s+/, $bestpath{$next_state_num});					
					if ($new_score > $cur_score)
					{
						$bestpath{$next_state_num} = "$state_num $new_score $cand";						
					}
				}
				else
				{
					$bestpath{$next_state_num} = "$state_num $new_score $cand";					
				}
				if ($new_score > $best_score)
				{
					$best_score = $new_score;
					$best_state_num = $next_state_num;
				}
			}
		}
		%states = %next_states;
	}

	my @best_parse;
	my $state_num = $best_state_num;
	while ($state_num != 0)
	{
		my ($prev, $score, $parse) = split(/\s+/, $bestpath{$state_num});
		unshift(@best_parse, $parse);
		$state_num = $prev;
	}
	#pop </s>
	pop(@best_parse);
	return ($best_score, @best_parse);
}

sub extract_features
{
	my ($feat_hash, @parse) = @_;
	
	unshift(@parse, "<s>");
	unshift(@parse, "<s>");
	push(@parse, "</s>");

	my $i;
	for ($i = 2; $i < @parse; ++$i)
	{
		my @trigram = ($parse[$i-2], $parse[$i-1], $parse[$i]);
		extract_trigram_feat($feat_hash, @trigram);
	}
}

sub extract_trigram_feat
{	
	my ($feat_hash, @trigram) = @_;

	$trigram[0] =~ /([^\+]+|[\+])(.*)/;
	my $r1 = $1;
	my @IG1 = split(/\^DB/, $2);

	$trigram[1] =~ /([^\+]+|[\+])(.*)/;
	my $r2 = $1;
	my @IG2 = split(/\^DB/, $2);

	$trigram[2] =~ /([^\+]+|[\+])(.*)/;
	my $r3 = $1;
	my @IG3 = split(/\^DB/, $2);

	$feat_hash->{"1:$r1@IG1-$r2@IG2-$r3@IG3"}++ if (!$exclude_feat{1});
	$feat_hash->{"2:$r1@IG2-$r3@IG3"}++ if (!$exclude_feat{2});
	$feat_hash->{"3:$r2@IG2-$r3@IG3"}++ if (!$exclude_feat{3});
	$feat_hash->{"4:$r3@IG3"}++ if (!$exclude_feat{4});
	$feat_hash->{"5:$r2@IG2-@IG3"}++ if (!$exclude_feat{5});	
	$feat_hash->{"6:$r1@IG1-@IG3"}++ if (!$exclude_feat{6});	
	$feat_hash->{"7:$r1-$r2-$r3"}++ if (!$exclude_feat{7});
	$feat_hash->{"8:$r1-$r3"}++ if (!$exclude_feat{8});
	$feat_hash->{"9:$r2-$r3"}++ if (!$exclude_feat{9});
	$feat_hash->{"10:$r3"}++ if (!$exclude_feat{10});
	$feat_hash->{"11:@IG1-@IG2-@IG3"}++ if (!$exclude_feat{11});
	$feat_hash->{"12:@IG1-@IG3"}++ if (!$exclude_feat{12});
	$feat_hash->{"13:@IG2-@IG3"}++ if (!$exclude_feat{13});
	$feat_hash->{"14:@IG3"}++ if (!$exclude_feat{14});
	foreach my $IG (@IG3)
	{
		$feat_hash->{"15:$IG1[$#IG1]-$IG2[$#IG2]-$IG"}++ if (!$exclude_feat{15});
		$feat_hash->{"16:$IG1[$#IG1]-$IG"}++ if (!$exclude_feat{16});
		$feat_hash->{"17:$IG2[$#IG2]-$IG"}++ if (!$exclude_feat{17});
		$feat_hash->{"18:$IG"}++ if (!$exclude_feat{18});
	}
	for (my $j = 0; $j < @IG3-1; ++$j)
	{
		$feat_hash->{"19:$IG3[$j]-$IG3[$j+1]"}++ if (!$exclude_feat{19});
	}
	for (my $j = 0; $j < @IG3; ++$j)
	{
		$feat_hash->{"20:$j-$IG3[$j]"}++ if (!$exclude_feat{20});
	}
	if ((($r3 =~ /^[A-Z]/) || ($r3 =~ /^[İĞÜÇÖŞ]/)) && ($trigram[2] =~ /Prop/))
	{
		$feat_hash->{"21:PROPER"}++ if (!$exclude_feat{21});
	}
	my $len = @IG3;
	$feat_hash->{"22:$len"}++ if (!$exclude_feat{22});
	if (($trigram[2] =~ /\.\+Punc/) && ($trigram[1] =~ /\+Verb\+/))
	{
		$feat_hash->{"23:ENDSVERB"}++ if (!$exclude_feat{23});
	}
}

sub score
{
	my ($feat_hash) = @_;
	
	my $score = 0;
	foreach my $feat (keys %{$feat_hash})
	{
		$score += $w{$feat} * $feat_hash->{$feat};
	}
	return $score;
}

sub ascore
{
	my ($feat_hash) = @_;
	
	my $score = 0;
	foreach my $feat (keys %{$feat_hash})
	{
		$score += $avgw{$feat} * $feat_hash->{$feat};
	}
	return $score;
}

sub update_model
{
	my ($feat_corr, $feat_best) = @_;
	
	my %featset;
	foreach my $feat (keys %{$feat_corr})
	{
		$featset{$feat} = 1;
	}
	foreach my $feat (keys %{$feat_best})
	{
		$featset{$feat} = 1;
	}
	foreach my $feat (keys %featset)
	{
		$avgw{$feat} = ($avgw{$feat} * $counts{$feat} + ($num_examples - $counts{$feat}) * $w{$feat})/$num_examples;
		$counts{$feat} = $num_examples;
		$w{$feat} += $feat_corr->{$feat} - $feat_best->{$feat};
		if ($avgw{$feat} == 0)
		{
			delete $avgw{$feat};
		}
		if ($w{$feat} == 0)
		{
			delete $w{$feat};
		}
	}
}

sub save_model
{
	my ($model) = @_;
	open(MODEL, "> $model") || die("cannot open file: $model\n");
	foreach my $feat (keys %avgw)
	{
		print MODEL "$avgw{$feat} $feat\n";
	}
	close(MODEL);
}

sub load_model
{
	my ($model) = @_;
	open(MODEL, $model) || die("cannot open file: $model\n");
	my $line;
	%avgw = ();
	while ($line = <MODEL>)
	{
		chomp($line);
		$line =~ /([^\s]*)\s+(.*)/;
		my $weight = $1;
		my $feat = $2;
		$avgw{$feat} = $weight;
	}
	close(MODEL);
}

sub read_sentence
{
	my ($FILE, $words, $correct_parse, $allparses) = @_;
	@{$words} = ();	
	@{$correct_parse} = ();
	@{$allparses} = ();
	
	my $line;
	while ($line = <$FILE>)
	{
		chomp($line);
		next if ($line =~ /<DOC>/);
		next if ($line =~ /<\/DOC>/);
		next if ($line =~ /<TITLE>/);
		next if ($line =~ /<\/TITLE>/);
		next if ($line =~ /<S>/);

		if ($line =~ /<\/S>/)
		{
			return 1;
		}
		my @tokens = split(/\s+/, $line);
		push(@{$words}, shift(@tokens));
		push(@{$correct_parse}, $tokens[0]);
		push(@{$allparses}, "@tokens");
	}
	return 0;
}
