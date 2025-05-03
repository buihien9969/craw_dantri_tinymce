<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('comments', function (Blueprint $table) {
            $table->id('comment_id');
            $table->foreignId('article_id')->constrained('articles', 'article_id');
            $table->foreignId('user_id')->constrained('users', 'user_id');
            $table->text('content');
            $table->integer('likes')->default(0);
            $table->integer('dislikes')->default(0);
            $table->enum('status', ['draft', 'approved', 'rejected'])->default('draft');
            $table->foreignId('parent_id')->nullable()->constrained('comments', 'comment_id');
            $table->integer('depth')->default(0);
            $table->timestamps();
        });

    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('comments');
    }
};
